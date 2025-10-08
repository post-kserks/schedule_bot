# utils/helpers.py
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

def validate_date(date_string: str) -> bool:
    """Проверяет корректность даты"""
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def get_date_for_weekday(weekday: str, reference_date: datetime) -> datetime:
    """Получает дату для указанного дня недели"""
    weekday_indices = {
        "понедельник": 0, "вторник": 1, "среда": 2, "четверг": 3,
        "пятница": 4, "суббота": 5, "воскресенье": 6
    }
    
    target_index = weekday_indices.get(weekday, 0)
    current_index = reference_date.weekday()
    
    days_difference = target_index - current_index
    if days_difference < 0:
        days_difference += 7
        
    return reference_date + timedelta(days=days_difference)