# services/admin_panel.py
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from src.services.database import db
from src.utils.config import ADMIN_USERNAME_LIST
from src.utils.keyboards import get_admin_menu_keyboard

logger = logging.getLogger(__name__)

class AdminPanel:
    def __init__(self):
        self.waiting_for_event_data = {}
        self.waiting_for_broadcast = set()
    
    def is_user_admin(self, username: str) -> bool:
        """Проверяет, является ли пользователь администратором"""
        if not username:
            return False
        clean_username = username.lstrip('@')
        return clean_username in ADMIN_USERNAME_LIST
    
    async def admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Главное меню админ-панели"""
        try:
            user = update.effective_user
            
            if not self.is_user_admin(user.username):
                if hasattr(update, 'message') and update.message:
                    await update.message.reply_text("❌ У вас нет прав для доступа к админ-панели")
                elif hasattr(update, 'callback_query') and update.callback_query:
                    await update.callback_query.message.reply_text("❌ У вас нет прав для доступа к админ-панели")
                return
            
            reply_markup = get_admin_menu_keyboard()
            
            if hasattr(update, 'message') and update.message:
                await update.message.reply_text(
                    "⚙️ Панель администратора\n\nВыберите действие:",
                    reply_markup=reply_markup
                )
            elif hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.message.edit_text(
                    "⚙️ Панель администратора\n\nВыберите действие:",
                    reply_markup=reply_markup
                )
        except Exception as e:
            logger.error(f"Ошибка в admin_menu: {e}")
            if hasattr(update, 'message') and update.message:
                await update.message.reply_text("❌ Произошла ошибка при открытии админ-панели")
    
    async def handle_admin_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback от админ-панели"""
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            if not self.is_user_admin(user.username):
                await query.edit_message_text("❌ У вас нет прав для доступа к админ-панели")
                return
            
            data = query.data
            
            # Очищаем состояние ожидания при любом возврате в меню или отмене
            if data in ["admin_back_to_menu", "admin_back_to_schedule"]:
                if user.id in self.waiting_for_event_data:
                    del self.waiting_for_event_data[user.id]
                if user.id in self.waiting_for_broadcast:
                    self.waiting_for_broadcast.discard(user.id)
            
            if data == "admin_list_events":
                await self._list_events(update, context)
            elif data == "admin_add_event":
                await self._start_add_event(update, context)
            elif data == "admin_delete_event":
                await self._start_delete_event(update, context)
            elif data == "admin_list_admins":
                await self._list_admins(update, context)
            elif data == "admin_broadcast_message":
                await self._start_broadcast_message(update, context)
            elif data.startswith("delete_event_"):
                event_id = int(data.split("_")[2])
                await self._confirm_delete_event(update, context, event_id)
            elif data.startswith("confirm_delete_"):
                event_id = int(data.split("_")[2])
                await self._execute_delete_event(update, context, event_id)
            elif data == "admin_back_to_schedule":
                await self._back_to_schedule(update, context)
            elif data == "admin_back_to_menu":
                await self.admin_menu(update, context)
                
        except Exception as e:
            logger.error(f"Ошибка в handle_admin_callback: {e}")
            try:
                query = update.callback_query
                await query.edit_message_text("❌ Произошла ошибка при обработке запроса")
            except:
                pass
    
    async def _list_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать список всех контрольных мероприятий"""
        try:
            query = update.callback_query
            events = db.get_all_control_events()
            
            if not events:
                await query.edit_message_text(
                    "📋 Список контрольных мероприятий пуст",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ Назад", callback_data="admin_back_to_menu")]
                    ])
                )
                return
            
            events_text = "📋 Все контрольные мероприятия:\n\n"
            for event in events:
                event_id, date, subject, event_type, created_by = event
                events_text += f"🆔 ID: {event_id}\n"
                events_text += f"📅 Дата: {date}\n"
                events_text += f"📚 Предмет: {subject}\n"
                events_text += f"🎯 Тип: {event_type}\n"
                events_text += f"👤 Добавил: {created_by or 'Неизвестно'}\n"
                events_text += "─" * 30 + "\n"
            
            await query.edit_message_text(
                events_text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Назад", callback_data="admin_back_to_menu")]
                ])
            )
        except Exception as e:
            logger.error(f"Ошибка в _list_events: {e}")
            await update.callback_query.edit_message_text("❌ Ошибка при получении списка мероприятий")
    
    async def _list_admins(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает список администраторов"""
        try:
            query = update.callback_query
            
            if not ADMIN_USERNAME_LIST:
                await query.edit_message_text(
                    "❌ Нет назначенных администраторов",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ Назад", callback_data="admin_back_to_menu")]
                    ])
                )
                return
            
            admin_info = "👥 Список администраторов:\n\n"
            
            for i, username in enumerate(ADMIN_USERNAME_LIST, 1):
                admin_info += f"{i}. @{username}\n"
            
            admin_info += f"\n📊 Всего администраторов: {len(ADMIN_USERNAME_LIST)}"
            
            await query.edit_message_text(
                admin_info,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Назад", callback_data="admin_back_to_menu")]
                ])
            )
        except Exception as e:
            logger.error(f"Ошибка в _list_admins: {e}")
            await update.callback_query.edit_message_text("❌ Ошибка при получении списка администраторов")
    
    async def _start_add_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать процесс добавления мероприятия"""
        try:
            query = update.callback_query
            
            # Сохраняем состояние для этого пользователя
            user_id = query.from_user.id
            self.waiting_for_event_data[user_id] = {"step": "waiting_for_date"}
            
            await query.edit_message_text(
                "➕ Добавление контрольного мероприятия\n\n"
                "Введите дату в формате ГГГГ-ММ-ДД (например, 2024-01-20):",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Отмена", callback_data="admin_back_to_menu")]
                ])
            )
        except Exception as e:
            logger.error(f"Ошибка в _start_add_event: {e}")
            await update.callback_query.edit_message_text("❌ Ошибка при начале добавления мероприятия")
    
    async def _start_broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать процесс отправки сообщения всем пользователям"""
        try:
            query = update.callback_query
            
            # Добавляем пользователя в состояние ожидания рассылки
            user_id = query.from_user.id
            self.waiting_for_broadcast.add(user_id)
            
            await query.edit_message_text(
                "📢 Отправка сообщения всем пользователям\n\n"
                "Введите текст сообщения, которое будет отправлено всем пользователям бота:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Отмена", callback_data="admin_back_to_menu")]
                ])
            )
        except Exception as e:
            logger.error(f"Ошибка в _start_broadcast_message: {e}")
            await update.callback_query.edit_message_text("❌ Ошибка при начале рассылки")
    
    async def _start_delete_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать процесс удаления мероприятия"""
        try:
            query = update.callback_query
            events = db.get_all_control_events()
            
            if not events:
                await query.edit_message_text(
                    "❌ Нет мероприятий для удаления",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ Назад", callback_data="admin_back_to_menu")]
                    ])
                )
                return
            
            keyboard = []
            for event in events:
                event_id, date, subject, event_type, _ = event
                keyboard.append([
                    InlineKeyboardButton(
                        f"❌ {date} - {subject}",
                        callback_data=f"delete_event_{event_id}"
                    )
                ])
            
            keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="admin_back_to_menu")])
            
            await query.edit_message_text(
                "❌ Выберите мероприятие для удаления:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"Ошибка в _start_delete_event: {e}")
            await update.callback_query.edit_message_text("❌ Ошибка при получении списка мероприятий для удаления")
    
    async def _confirm_delete_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE, event_id: int):
        """Подтверждение удаления мероприятия"""
        try:
            query = update.callback_query
            events = db.get_all_control_events()
            event_to_delete = None
            
            for event in events:
                if event[0] == event_id:
                    event_to_delete = event
                    break
            
            if not event_to_delete:
                await query.edit_message_text("❌ Мероприятие не найдено")
                return
            
            _, date, subject, event_type, _ = event_to_delete
            
            await query.edit_message_text(
                f"⚠️ Подтвердите удаление:\n\n"
                f"📅 Дата: {date}\n"
                f"📚 Предмет: {subject}\n"
                f"🎯 Тип: {event_type}\n\n"
                f"Вы уверены, что хотите удалить это мероприятие?",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ Да", callback_data=f"confirm_delete_{event_id}"),
                        InlineKeyboardButton("❌ Нет", callback_data="admin_back_to_menu")
                    ]
                ])
            )
        except Exception as e:
            logger.error(f"Ошибка в _confirm_delete_event: {e}")
            await update.callback_query.edit_message_text("❌ Ошибка при подтверждении удаления")
    
    async def _execute_delete_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE, event_id: int):
        """Выполнить удаление мероприятия"""
        try:
            query = update.callback_query
            
            if db.delete_control_event(event_id):
                await query.edit_message_text(
                    "✅ Мероприятие успешно удалено",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ В меню", callback_data="admin_back_to_menu")]
                    ])
                )
            else:
                await query.edit_message_text(
                    "❌ Ошибка при удалении мероприятия",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ В меню", callback_data="admin_back_to_menu")]
                    ])
                )
        except Exception as e:
            logger.error(f"Ошибка в _execute_delete_event: {e}")
            await update.callback_query.edit_message_text("❌ Ошибка при удалении мероприятия")
    
    async def _execute_broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Выполнить рассылку сообщения всем пользователям"""
        try:
            users = db.get_all_users()
            
            if not users:
                await update.message.reply_text("❌ Нет пользователей для рассылки")
                return
            
            success_count = 0
            fail_count = 0
            
            # Отправляем сообщение о начале рассылки
            progress_msg = await update.message.reply_text("🔄 Начинаю рассылку сообщения...")
            
            for user_id in users:
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"📢 Объявление от администратора:\n\n{message_text}"
                    )
                    success_count += 1
                except Exception as e:
                    logger.warning(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
                    fail_count += 1
            
            report_text = (
                f"📊 Результат рассылки:\n"
                f"✅ Успешно: {success_count}\n"
                f"❌ Не удалось: {fail_count}\n"
                f"👥 Всего пользователей: {len(users)}"
            )
            
            await progress_msg.edit_text(report_text)
            
        except Exception as e:
            logger.error(f"Ошибка при рассылке сообщений: {e}")
            await update.message.reply_text("❌ Произошла ошибка при рассылке")
    
    async def _back_to_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Вернуться к основному расписанию"""
        try:
            query = update.callback_query
            
            # Очищаем состояние ожидания при возврате к расписанию
            user_id = query.from_user.id
            if user_id in self.waiting_for_event_data:
                del self.waiting_for_event_data[user_id]
            if user_id in self.waiting_for_broadcast:
                self.waiting_for_broadcast.discard(user_id)
            
            await query.edit_message_text("🔄 Возврат к основному расписанию...")
            
            # Импортируем здесь, чтобы избежать циклического импорта
            from src.handlers.user_handlers import ScheduleBot
            
            # Создаем временный экземпляр бота для доступа к методам клавиатуры
            temp_bot = ScheduleBot("dummy_token")
            user = query.from_user
            
            if self.is_user_admin(user.username):
                keyboard = temp_bot.get_admin_keyboard()
            else:
                keyboard = temp_bot.get_main_keyboard()
            
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="Вы вернулись в главное меню. Используйте кнопки ниже:",
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка в _back_to_schedule: {e}")
            await update.callback_query.edit_message_text("❌ Ошибка при возврате к расписанию")
    
    async def handle_admin_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик сообщений для админ-панели"""
        try:
            user = update.effective_user
            
            if not self.is_user_admin(user.username):
                await update.message.reply_text("❌ У вас нет прав для выполнения этой операции")
                return
            
            user_id = user.id
            message_text = update.message.text
            
            # Если пользователь в состоянии рассылки
            if user_id in self.waiting_for_broadcast:
                # Удаляем из состояния рассылки
                self.waiting_for_broadcast.discard(user_id)
                # Выполняем рассылку
                await self._execute_broadcast_message(update, context, message_text)
                # Возвращаем в меню
                await self.admin_menu(update, context)
                return
            
            # Если пользователь в процессе добавления мероприятия
            if user_id in self.waiting_for_event_data:
                step_data = self.waiting_for_event_data[user_id]
                
                # Проверяем, не хочет ли пользователь отменить операцию
                if message_text.lower() in ['отмена', 'cancel', 'назад']:
                    # Очищаем состояние
                    del self.waiting_for_event_data[user_id]
                    await update.message.reply_text("❌ Добавление мероприятия отменено.")
                    await self.admin_menu(update, context)
                    return
                
                if step_data["step"] == "waiting_for_date":
                    # Проверяем формат даты
                    try:
                        datetime.strptime(message_text, "%Y-%m-%d")
                        step_data["date"] = message_text
                        step_data["step"] = "waiting_for_subject"
                        await update.message.reply_text("📚 Теперь введите название предмета:")
                    except ValueError:
                        await update.message.reply_text("❌ Неверный формат даты. Используйте ГГГГ-ММ-ДД:")
                
                elif step_data["step"] == "waiting_for_subject":
                    if not message_text.strip():
                        await update.message.reply_text("❌ Название предмета не может быть пустым. Введите название предмета:")
                        return
                    
                    step_data["subject"] = message_text.strip()
                    step_data["step"] = "waiting_for_event_type"
                    await update.message.reply_text("🎯 Теперь введите тип мероприятия (например, 'контрольная работа', 'домашняя работа'):")
                
                elif step_data["step"] == "waiting_for_event_type":
                    if not message_text.strip():
                        await update.message.reply_text("❌ Тип мероприятия не может быть пустым. Введите тип мероприятия:")
                        return
                    
                    step_data["event_type"] = message_text.strip()
                    
                    # Сохраняем мероприятие в БД
                    event_id = db.add_control_event(
                        step_data["date"],
                        step_data["subject"],
                        step_data["event_type"],
                        user.username
                    )
                    
                    if event_id:
                        await update.message.reply_text(
                            f"✅ Мероприятие успешно добавлено!\n\n"
                            f"📅 Дата: {step_data['date']}\n"
                            f"📚 Предмет: {step_data['subject']}\n"
                            f"🎯 Тип: {step_data['event_type']}"
                        )
                    else:
                        await update.message.reply_text("❌ Ошибка при добавлении мероприятия в базу данных")
                    
                    # Очищаем состояние
                    del self.waiting_for_event_data[user_id]
                    
                    # Возвращаем в админ-меню
                    await self.admin_menu(update, context)
        except Exception as e:
            logger.error(f"Ошибка в handle_admin_message: {e}")
            await update.message.reply_text("❌ Произошла ошибка при обработке запроса")

# Глобальный экземпляр админ-панели
admin_panel = AdminPanel()