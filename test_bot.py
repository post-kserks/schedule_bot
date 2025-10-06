# test_bot.py
import asyncio
import logging
from database import db
from schedule import schedule_manager
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_all_functionality():
    """Тестирует весь функционал бота"""
    print("🧪 Начинаем тестирование функционала бота...\n")
    
    # 1. Тест базы данных
    print("1. Тестируем базу данных...")
    try:
        # Добавляем тестовое событие
        test_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        event_id = db.add_control_event(test_date, "Математический анализ", "Контрольная работа", "test")
        
        # Проверяем добавление
        events = db.get_control_events_by_date(test_date)
        if events:
            print("✅ База данных работает корректно")
        else:
            print("❌ Ошибка в работе базы данных")
        
        # Удаляем тестовое событие
        db.delete_control_event(event_id)
    except Exception as e:
        print(f"❌ Ошибка тестирования БД: {e}")
    
    # 2. Тест расписания
    print("\n2. Тестируем модуль расписания...")
    try:
        today_schedule = schedule_manager.get_today_schedule()
        tomorrow_schedule = schedule_manager.get_tomorrow_schedule()
        
        if today_schedule and tomorrow_schedule:
            print("✅ Модуль расписания работает корректно")
            print(f"   Сегодня: {len(today_schedule)} символов")
            print(f"   Завтра: {len(tomorrow_schedule)} символов")
        else:
            print("❌ Ошибка в модуле расписания")
    except Exception as e:
        print(f"❌ Ошибка тестирования расписания: {e}")
    
    # 3. Тест определения типа недели
    print("\n3. Тестируем определение типа недели...")
    try:
        is_num = schedule_manager.is_numerator_week()
        week_type = "Числитель" if is_num else "Знаменатель"
        print(f"✅ Текущая неделя: {week_type}")
    except Exception as e:
        print(f"❌ Ошибка определения типа недели: {e}")
    
    # 4. Тест получения предметов
    print("\n4. Тестируем получение предметов...")
    try:
        subjects = schedule_manager.get_subjects_with_times()
        if subjects:
            print(f"✅ Получено {len(subjects)} предметов на сегодня")
            for subj in subjects[:2]:  # Показываем первые 2
                print(f"   - {subj['name']} в {subj['start_time']}")
        else:
            print("❌ Не удалось получить предметы")
    except Exception as e:
        print(f"❌ Ошибка получения предметов: {e}")
    
    print("\n🎉 Тестирование завершено!")

if __name__ == "__main__":
    asyncio.run(test_all_functionality())