# notifier.py
import logging
import asyncio
from datetime import datetime, timedelta
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from telegram import KeyboardButton, ReplyKeyboardMarkup
from schedule import schedule_manager
from database import db

logger = logging.getLogger(__name__)

class Notifier:
    def __init__(self, application):
        self.application = application
        self.job_queue = application.job_queue
    
    # notifier.py (обновляем метод send_daily_schedule)
    async def send_daily_schedule(self, context: ContextTypes.DEFAULT_TYPE):
        """Отправляет расписание на завтрашний день всем пользователям"""
        try:
            tomorrow_schedule = schedule_manager.get_tomorrow_schedule()
            users = db.get_all_users()
            
            if not users:
                logger.info("Нет пользователей для отправки расписания")
                return
            
            # Создаем клавиатуру для уведомлений (с новой кнопкой)
            keyboard = [
                [KeyboardButton("📅 Сегодня"), KeyboardButton("📆 Завтра")],
                [KeyboardButton("📅 Неделя"), KeyboardButton("❓ Помощь")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            success_count = 0
            for user_id in users:
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=tomorrow_schedule,
                        reply_markup=reply_markup
                    )
                    success_count += 1
                    # Небольшая задержка чтобы не превысить лимиты Telegram
                    await asyncio.sleep(0.1)
                except TelegramError as e:
                    logger.warning(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
                    # Если пользователь заблокировал бота, можно удалить его из БД
                    if "bot was blocked" in str(e).lower():
                        logger.info(f"Пользователь {user_id} заблокировал бота")
            
            logger.info(f"Ежедневное расписание отправлено {success_count}/{len(users)} пользователям")
            
        except Exception as e:
            logger.error(f"Ошибка отправки ежедневного расписания: {e}")
    
    async def check_upcoming_lessons(self, context: ContextTypes.DEFAULT_TYPE):
        """Проверяет ближайшие занятия и отправляет уведомления"""
        try:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_date = now.strftime("%Y-%m-%d")
            
            # Получаем расписание на сегодня
            subjects = schedule_manager.get_subjects_with_times(now)
            
            for subject in subjects:
                start_time = subject['start_time']
                subject_name = subject['name']
                room = subject['room']
                lesson_type = subject['type']
                
                # Вычисляем время за 10 минут до начала
                start_dt = datetime.strptime(start_time, "%H:%M")
                reminder_time = (start_dt - timedelta(minutes=10)).strftime("%H:%M")
                
                # Если текущее время совпадает с временем напоминания
                if current_time == reminder_time:
                    message = (
                        f"🔔 Напоминание!\n"
                        f"Через 10 минут начинается:\n"
                        f"📚 {subject_name}\n"
                        f"🏫 {room}\n"
                        f"📝 {lesson_type}\n"
                        f"⏰ {start_time}"
                    )
                    
                    # Отправляем всем пользователям
                    users = db.get_all_users()
                    success_count = 0
                    
                    for user_id in users:
                        try:
                            await context.bot.send_message(
                                chat_id=user_id,
                                text=message
                            )
                            success_count += 1
                            await asyncio.sleep(0.1)
                        except TelegramError as e:
                            logger.warning(f"Не удалось отправить напоминание пользователю {user_id}: {e}")
                    
                    logger.info(f"Напоминание отправлено {success_count}/{len(users)} пользователям: {subject_name} в {start_time}")
                    
        except Exception as e:
            logger.error(f"Ошибка проверки ближайших занятий: {e}")
    
    def setup_jobs(self):
        """Настраивает регулярные задания"""
        if self.job_queue:
            # Ежедневная отправка расписания в 21:00
            self.job_queue.run_daily(
                self.send_daily_schedule,
                time=datetime.strptime("21:00", "%H:%M").time(),
                name="daily_schedule"
            )
            
            # Проверка ближайших занятий каждую минуту
            self.job_queue.run_repeating(
                self.check_upcoming_lessons,
                interval=60,  # 60 секунд = 1 минута
                first=10,     # Начать через 10 секунд после запуска
                name="lesson_reminders"
            )
            
            logger.info("Регулярные задания настроены")
        else:
            logger.warning("JobQueue не доступен. Регулярные задания не настроены.")