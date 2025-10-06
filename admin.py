# admin.py
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import db
from config import ADMIN_USERNAME_LIST

logger = logging.getLogger(__name__)

class AdminPanel:
    def __init__(self):
        self.waiting_for_event_data = {}
    
    def is_user_admin(self, username: str) -> bool:
        """Проверяет, является ли пользователь администратором"""
        if not username:
            return False
        
        # Проверка по username (без @)
        clean_username = username.lstrip('@')
        return clean_username in ADMIN_USERNAME_LIST
    
    async def admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Главное меню админ-панели"""
        user = update.effective_user
        
        if not self.is_user_admin(user.username):
            await update.message.reply_text("❌ У вас нет прав для доступа к админ-панели")
            return
        
        keyboard = [
            [InlineKeyboardButton("📋 Список мероприятий", callback_data="admin_list_events")],
            [InlineKeyboardButton("➕ Добавить мероприятие", callback_data="admin_add_event")],
            [InlineKeyboardButton("❌ Удалить мероприятие", callback_data="admin_delete_event")],
            [InlineKeyboardButton("👥 Список админов", callback_data="admin_list_admins")],
            [InlineKeyboardButton("⬅️ Назад к расписанию", callback_data="admin_back_to_schedule")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
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
    
    async def handle_admin_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback от админ-панели"""
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
        
        if data == "admin_list_events":
            await self._list_events(update, context)
        elif data == "admin_add_event":
            await self._start_add_event(update, context)
        elif data == "admin_delete_event":
            await self._start_delete_event(update, context)
        elif data == "admin_list_admins":
            await self._list_admins(update, context)
        elif data.startswith("delete_event_"):
            event_id = int(data.split("_")[2])
            await self._confirm_delete_event(update, context, event_id)
        elif data.startswith("confirm_delete_"):
            event_id = int(data.split("_")[2])
            await self._execute_delete_event(update, context, event_id)
        elif data == "admin_back_to_schedule":
            await self._back_to_schedule(update, context)
        elif data == "admin_back_to_menu":
            await self._back_to_menu(update, context)
    
    async def _list_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать список всех контрольных мероприятий"""
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
    
    async def _list_admins(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает список администраторов"""
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
    
    async def _start_add_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать процесс добавления мероприятия"""
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
    
    async def _start_delete_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать процесс удаления мероприятия"""
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
    
    async def _confirm_delete_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE, event_id: int):
        """Подтверждение удаления мероприятия"""
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
    
    async def _execute_delete_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE, event_id: int):
        """Выполнить удаление мероприятия"""
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
    
    async def _back_to_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Вернуться в главное меню"""
        query = update.callback_query
        
        # Очищаем состояние ожидания при возврате в меню
        user_id = query.from_user.id
        if user_id in self.waiting_for_event_data:
            del self.waiting_for_event_data[user_id]
            
        await self.admin_menu_from_query(query)
    
    async def _back_to_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Вернуться к основному расписанию"""
        query = update.callback_query
        
        # Очищаем состояние ожидания при возврате к расписанию
        user_id = query.from_user.id
        if user_id in self.waiting_for_event_data:
            del self.waiting_for_event_data[user_id]
        
        await query.edit_message_text("Возврат к основному расписанию...")
        
        # Импортируем здесь, чтобы избежать циклического импорта
        from bot import ScheduleBot
        
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
    
    async def admin_menu_from_query(self, query):
        """Показать меню админа из callback query"""
        keyboard = [
            [InlineKeyboardButton("📋 Список мероприятий", callback_data="admin_list_events")],
            [InlineKeyboardButton("➕ Добавить мероприятие", callback_data="admin_add_event")],
            [InlineKeyboardButton("❌ Удалить мероприятие", callback_data="admin_delete_event")],
            [InlineKeyboardButton("👥 Список админов", callback_data="admin_list_admins")],
            [InlineKeyboardButton("⬅️ Назад к расписанию", callback_data="admin_back_to_schedule")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚙️ Панель администратора\n\n"
            "Выберите действие:",
            reply_markup=reply_markup
        )
    
    async def handle_admin_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик сообщений для админ-панели"""
        user = update.effective_user
        
        if not self.is_user_admin(user.username):
            return
        
        user_id = user.id
        message_text = update.message.text
        
        # Проверяем, находится ли пользователь в процессе диалога
        if user_id not in self.waiting_for_event_data:
            # Если пользователь не в процессе добавления мероприятия, но написал сообщение,
            # возможно, он пытается отменить операцию
            if message_text.lower() in ['отмена', 'cancel', 'назад']:
                await update.message.reply_text("Операция отменена.")
                await self.admin_menu(update, context)
            return
        
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
            step_data["subject"] = message_text
            step_data["step"] = "waiting_for_event_type"
            await update.message.reply_text("🎯 Теперь введите тип мероприятия (например, 'контрольная работа', 'домашняя работа'):")
        
        elif step_data["step"] == "waiting_for_event_type":
            step_data["event_type"] = message_text
            
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
                await update.message.reply_text("❌ Ошибка при добавлении мероприятия")
            
            # Очищаем состояние
            del self.waiting_for_event_data[user_id]
            
            # Возвращаем в админ-меню
            await self.admin_menu(update, context)

# Глобальный экземпляр админ-панели
admin_panel = AdminPanel()