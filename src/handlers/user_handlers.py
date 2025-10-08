# handlers/user_handlers.py
import logging
from datetime import datetime
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from telegram import Update, ReplyKeyboardRemove
from src.utils.config import BOT_TOKEN
from src.services.database import db
from src.services.schedule_manager import schedule_manager
from src.services.notifier import Notifier
from src.services.admin_panel import admin_panel
from src.utils.keyboards import get_main_keyboard, get_admin_keyboard
from src.utils.helpers import setup_logging

logger = logging.getLogger(__name__)

class ScheduleBot:
    def __init__(self, token: str):
        self.application = Application.builder().token(token).build()
        self.notifier = Notifier(self.application)
        setup_logging()
    
    def is_user_admin(self, username: str) -> bool:
        """Проверяет, является ли пользователь администратором"""
        return admin_panel.is_user_admin(username)
    
    def get_main_keyboard(self):
        """Возвращает основную клавиатуру с кнопками"""
        return get_main_keyboard()
    
    def get_admin_keyboard(self):
        """Возвращает клавиатуру для администратора"""
        return get_admin_keyboard()
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user = update.effective_user
            db.add_user(user.id, user.username, user.first_name, user.last_name)
            
            welcome_text = (
                "📚 Бот расписания активирован\n\n"
                "Я буду присылать:\n"
                "• 📅 Расписание на завтра каждый день в 21:00\n"
                "• 🔔 Напоминания за 10 минут до начала занятий\n\n"
                "Используйте кнопки ниже для навигации:"
            )
            
            if self.is_user_admin(user.username):
                keyboard = self.get_admin_keyboard()
                welcome_text += "\n\n⚙️ Доступна админ-панель"
            else:
                keyboard = self.get_main_keyboard()
            
            await update.message.reply_text(welcome_text, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Ошибка в команде /start: {e}")
            await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        await self.help(update, context)
        
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None):
        """Показывает справку"""
        help_text = """
📋 Доступные команды:

📅 Сегодня - Расписание на сегодня
📆 Завтра - Расписание на завтра
📅 Неделя - Расписание на всю неделю
❓ Помощь - Эта справка

Для администраторов:
⚙️ Админ-панель - Управление мероприятиями
        """
        
        if hasattr(update, 'message') and update.message:
            user = update.effective_user
            if self.is_user_admin(user.username):
                keyboard = self.get_admin_keyboard()
            else:
                keyboard = self.get_main_keyboard()
            await update.message.reply_text(help_text, reply_markup=keyboard)
        elif hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.message.reply_text(help_text)
    
    async def today_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /today"""
        await self.today(update, context)
        
    async def today(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None):
        """Показывает расписание на сегодня"""
        try:
            current_date = datetime.now()
            logger.info(f"Запрос расписания на сегодня: {current_date}, день недели: {current_date.weekday()}")
            
            schedule_text = schedule_manager.get_today_schedule()
            
            if hasattr(update, 'message') and update.message:
                user = update.effective_user
                if self.is_user_admin(user.username):
                    keyboard = self.get_admin_keyboard()
                else:
                    keyboard = self.get_main_keyboard()
                await update.message.reply_text(schedule_text, reply_markup=keyboard)
            elif hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.message.reply_text(schedule_text)
                
        except Exception as e:
            logger.error(f"Ошибка в команде /today: {e}")
            error_msg = "❌ Не удалось получить расписание на сегодня."
            if hasattr(update, 'message') and update.message:
                await update.message.reply_text(error_msg)
            elif hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.message.reply_text(error_msg)
    
    async def tomorrow_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /tomorrow"""
        await self.tomorrow(update, context)
        
    async def tomorrow(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None):
        """Показывает расписание на завтра"""
        try:
            schedule_text = schedule_manager.get_tomorrow_schedule()
            
            if hasattr(update, 'message') and update.message:
                user = update.effective_user
                if self.is_user_admin(user.username):
                    keyboard = self.get_admin_keyboard()
                else:
                    keyboard = self.get_main_keyboard()
                await update.message.reply_text(schedule_text, reply_markup=keyboard)
            elif hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.message.reply_text(schedule_text)
                
        except Exception as e:
            logger.error(f"Ошибка в команде /tomorrow: {e}")
            error_msg = "❌ Не удалось получить расписание на завтра."
            if hasattr(update, 'message') and update.message:
                await update.message.reply_text(error_msg)
            elif hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.message.reply_text(error_msg)
    
    async def week_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /week"""
        await self.week(update, context)
        
    async def week(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None):
        """Показывает расписание на неделю"""
        try:
            week_schedule = schedule_manager.get_week_schedule()
            
            if hasattr(update, 'message') and update.message:
                user = update.effective_user
                if self.is_user_admin(user.username):
                    keyboard = self.get_admin_keyboard()
                else:
                    keyboard = self.get_main_keyboard()
                await update.message.reply_text(week_schedule, reply_markup=keyboard)
            elif hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.message.reply_text(week_schedule)
                
        except Exception as e:
            logger.error(f"Ошибка в команде расписания на неделю: {e}")
            error_msg = "❌ Не удалось получить расписание на неделю."
            if hasattr(update, 'message') and update.message:
                await update.message.reply_text(error_msg)
            elif hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.message.reply_text(error_msg)
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /admin"""
        await self.admin(update, context)
        
    async def admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None):
        """Команда для открытия админ-панели"""
        user = update.effective_user
        
        if not self.is_user_admin(user.username):
            await update.message.reply_text("❌ У вас нет прав для доступа к админ-панели")
            return
        
        await update.message.reply_text("🔄 Переход в админ-панель...", reply_markup=ReplyKeyboardRemove())
        await admin_panel.admin_menu(update, context)
    
    async def get_my_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает информацию о пользователе"""
        user = update.effective_user
        is_admin = self.is_user_admin(user.username)
        
        admin_status = "✅ Администратор" if is_admin else "❌ Обычный пользователь"
        
        message = (
            f"👤 Ваши данные:\n"
            f"🆔 ID: `{user.id}`\n"
            f"📛 Username: @{user.username or 'не установлен'}\n"
            f"📝 Имя: {user.first_name or ''} {user.last_name or ''}\n"
            f"🔐 Статус: {admin_status}\n\n"
        )
        
        if is_admin:
            message += "Доступны функции админ-панели: управление мероприятиями"
        else:
            message += "Для получения прав администратора обратитесь к текущим админам"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений (для кнопок)"""
        try:
            user = update.effective_user
            text = update.message.text
            
            logger.info(f"Получено сообщение от {user.username}: {text}")
            
            # Сначала проверяем, находится ли пользователь в диалоге с админ-панелью
            if self.is_user_admin(user.username):
                if user.id in admin_panel.waiting_for_event_data or user.id in admin_panel.waiting_for_broadcast:
                    await admin_panel.handle_admin_message(update, context)
                    return
            
            # Затем обрабатываем обычные команды
            if text == "📅 Сегодня":
                await self.today(update, context)
            elif text == "📆 Завтра":
                await self.tomorrow(update, context)
            elif text == "📅 Неделя":
                await self.week(update, context)
            elif text == "❓ Помощь":
                await self.help(update, context)
            elif text == "⚙️ Админ-панель":
                if self.is_user_admin(user.username):
                    await self.admin(update, context)
                else:
                    await update.message.reply_text("❌ У вас нет прав для доступа к админ-панели")
            else:
                # Если сообщение не распознано, показываем помощь
                await self.help(update, context)
        except Exception as e:
            logger.error(f"Ошибка в handle_text_message: {e}")
            await update.message.reply_text("❌ Произошла ошибка при обработке сообщения")
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback запросов от инлайн-кнопок"""
        try:
            query = update.callback_query
            await query.answer()
            
            # Передаем обработку в админ-панель
            await admin_panel.handle_admin_callback(update, context)
        except Exception as e:
            logger.error(f"Ошибка в handle_callback_query: {e}")
            try:
                await update.callback_query.message.reply_text("❌ Произошла ошибка при обработке запроса")
            except:
                pass
    
    def setup_handlers(self):
        """Настраивает обработчики команд"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("today", self.today_command))
        self.application.add_handler(CommandHandler("tomorrow", self.tomorrow_command))
        self.application.add_handler(CommandHandler("week", self.week_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CommandHandler("myinfo", self.get_my_info))
        
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
    
    def run(self):
        """Запускает бота"""
        self.setup_handlers()
        self.notifier.setup_jobs()
        
        logger.info("Бот успешно запущен")
        print("🤖 Бот запущен и готов к работе!")
        
        self.application.run_polling()