# services/notifier.py
import logging
import asyncio
from datetime import datetime, timedelta
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from src.services.schedule_manager import schedule_manager
from src.services.database import db
from src.utils.keyboards import get_main_keyboard

logger = logging.getLogger(__name__)

class Notifier:
    def __init__(self, application):
        self.application = application
        self.job_queue = application.job_queue
    
    async def send_daily_schedule(self, context: ContextTypes.DEFAULT_TYPE):
        """Отправляет расписание на завтрашний день всем пользователям"""
        try:
            # Логируем текущее время для отладки
            now_utc = datetime.utcnow()
            now_moscow = now_utc + timedelta(hours=3)  # UTC+3 для Москвы
            logger.info(f"🕘 Запуск отправки ежедневного расписания. Время: UTC {now_utc.strftime('%H:%M')}, Moscow {now_moscow.strftime('%H:%M')}")
            
            tomorrow_schedule = schedule_manager.get_tomorrow_schedule()
            users = db.get_all_users()
            
            if not users:
                logger.info("❌ Нет пользователей для отправки расписания")
                return
            
            logger.info(f"📤 Найдено {len(users)} пользователей для рассылки")
            
            reply_markup = get_main_keyboard()
            success_count = 0
            fail_count = 0
            
            # Отправляем сообщение о начале рассылки (первому пользователю)
            if users:
                try:
                    await context.bot.send_message(
                        chat_id=users[0],
                        text=f"🔄 Начинаю рассылку расписания на завтра для {len(users)} пользователей..."
                    )
                except:
                    pass
            
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
                    logger.warning(f"❌ Не удалось отправить сообщение пользователю {user_id}: {e}")
                    fail_count += 1
                    if "bot was blocked" in str(e).lower():
                        logger.info(f"🚫 Пользователь {user_id} заблокировал бота")
            
            # Логируем результат
            result_msg = f"✅ Ежедневное расписание отправлено: Успешно {success_count}, Не удалось {fail_count}"
            logger.info(result_msg)
            
            # Отправляем отчет первому пользователю
            if users and success_count > 0:
                try:
                    await context.bot.send_message(
                        chat_id=users[0],
                        text=result_msg
                    )
                except:
                    pass
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка отправки ежедневного расписания: {e}")
    
    async def check_upcoming_lessons(self, context: ContextTypes.DEFAULT_TYPE):
        """Проверяет ближайшие занятия и отправляет уведомления"""
        try:
            now_utc = datetime.utcnow()
            now_moscow = now_utc + timedelta(hours=3)
            current_time = now_moscow.strftime("%H:%M")
            current_date = now_moscow.strftime("%Y-%m-%d")
            
            logger.debug(f"🔍 Проверка ближайших занятий: Moscow {current_time}")
            
            # Используем московское время для получения расписания
            subjects = schedule_manager.get_subjects_with_times(now_moscow)
            
            if not subjects:
                logger.debug("📭 На сегодня занятий нет")
                return
            
            for subject in subjects:
                start_time = subject['start_time']
                subject_name = subject['name']
                room = subject['room']
                lesson_type = subject['type']
                
                # Вычисляем время за 10 минут до начала (в московском времени)
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
                    
                    logger.info(f"⏰ Отправка напоминания: {subject_name} в {start_time}")
                    
                    # Отправляем всем пользователям
                    users = db.get_all_users()
                    success_count = 0
                    fail_count = 0
                    
                    for user_id in users:
                        try:
                            await context.bot.send_message(
                                chat_id=user_id,
                                text=message
                            )
                            success_count += 1
                            await asyncio.sleep(0.1)
                        except TelegramError as e:
                            logger.warning(f"❌ Не удалось отправить напоминание пользователю {user_id}: {e}")
                            fail_count += 1
                    
                    logger.info(f"✅ Напоминание отправлено: Успешно {success_count}, Не удалось {fail_count}")
                    
        except Exception as e:
            logger.error(f"❌ Ошибка проверки ближайших занятий: {e}")
    
    def setup_jobs(self):
        """Настраивает регулярные задания"""
        try:
            if not self.job_queue:
                logger.error("❌ JobQueue не доступна!")
                return
            
            logger.info("⚙️ Настройка регулярных заданий...")
            
            # Очищаем старые задания
            for job in self.job_queue.jobs():
                self.job_queue.scheduler.remove_job(job.id)
            
            # Ежедневная отправка расписания в 21:00 по Москве
            # В Docker установлена TZ=Europe/Moscow, поэтому используем локальное время
            self.job_queue.run_daily(
                self.send_daily_schedule,
                time=datetime.strptime("21:00", "%H:%M").time(),  # 21:00 Moscow Time
                name="daily_schedule",
                days=tuple(range(7))  # Все дни недели
            )
            logger.info("✅ Задание 'daily_schedule' настроено на 21:00 Moscow Time")
            
            # Проверка ближайших занятий каждую минуту
            self.job_queue.run_repeating(
                self.check_upcoming_lessons,
                interval=60,  # 60 секунд = 1 минута
                first=5,      # Начать через 5 секунд после запуска
                name="lesson_reminders"
            )
            logger.info("✅ Задание 'lesson_reminders' настроено")
            
            # Тестовое задание - запустить через 1 минуту после старта для проверки
            self.job_queue.run_once(
                self._test_notification,
                when=60,  # 60 секунд = 1 минута
                name="test_notification"
            )
            logger.info("✅ Тестовое задание 'test_notification' настроено")
            
            # Логируем следующее выполнение daily_schedule
            for job in self.job_queue.jobs():
                if job.name == "daily_schedule":
                    logger.info(f"📅 Следующая отправка расписания: {job.next_t}")
            
            logger.info("🎯 Все регулярные задания успешно настроены")
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки регулярных заданий: {e}")
    
#    async def _test_notification(self, context: ContextTypes.DEFAULT_TYPE):
#        """Тестовая отправка уведомления для проверки работы"""
#        try:
#            now_utc = datetime.utcnow()
#            now_moscow = now_utc + timedelta(hours=3)
#            logger.info(f"🧪 Запуск тестового уведомления. Moscow time: {now_moscow.strftime('%Y-%m-%d %H:%M:%S')}")
#            
#            users = db.get_all_users()
#            if users:
#                test_message = (
#                    "🧪 Тестовое уведомление\n"
#                    f"🕒 Время сервера: {now_moscow.strftime('%Y-%m-%d %H:%M:%S')}\n"
#                    "✅ Бот успешно запущен и готов к работе!\n"
#                    "✅ Регулярные задания настроены\n"
#                    "✅ Расписание загружено\n"
#                    "✅ База данных работает\n\n"
#                    "📅 Завтрашнее расписание будет отправлено в 21:00"
#                )
#                
#                await context.bot.send_message(
#                    chat_id=users[0],  # Отправляем первому пользователю
#                    text=test_message
#                )
#                logger.info("✅ Тестовое уведомление отправлено")
#            else:
#                logger.info("📭 Нет пользователей для тестового уведомления")
#                
#        except Exception as e:
#            logger.error(f"❌ Ошибка тестового уведомления: {e}")