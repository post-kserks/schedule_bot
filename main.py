# main.py
import logging
import sys
import os

# Добавляем корневую директорию в путь для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.handlers.user_handlers import ScheduleBot
from src.utils.config import BOT_TOKEN
from src.utils.helpers import setup_logging

def main():
    """Основная функция запуска бота"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        bot = ScheduleBot(BOT_TOKEN)
        print("🚀 Бот запускается...")
        bot.run()
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        print(f"❌ Ошибка запуска: {e}")

if __name__ == '__main__':
    main()