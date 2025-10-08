# services/schedule_manager.py
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from src.models.schedule_models import Subject, DaySchedule
from src.services.database import db

logger = logging.getLogger(__name__)

class ScheduleManager:
    """Менеджер расписания"""
    
    def __init__(self):
        self.numerator_schedule = self._parse_numerator_schedule()
        self.denominator_schedule = self._parse_denominator_schedule()
        self.semester_start = datetime(2024, 9, 1)
    
    def _parse_numerator_schedule(self) -> Dict[str, DaySchedule]:
        """Парсинг расписания для числителя"""
        return {
            "понедельник": DaySchedule("понедельник", [
                Subject("Практика иу5", "903", "10:10", "11:40", "семинар"),
                Subject("Практика иу5", "903", "11:50", "13:55", "семинар"),
                Subject("Основы программирования", "301х", "14:05", "15:35", "лекция"),
                Subject("Основы программирования", "301х", "14:05", "15:35", "лекция")
            ]),
            "вторник": DaySchedule("вторник", [
                Subject("Математический анализ", "301х", "10:10", "11:40", "лекция"),
                Subject("Основы программирования", "524к", "12:25", "13:55", "лабораторная работа"),
                Subject("История России", "618к", "14:05", "15:35", "семинар"),
                Subject("Информатика", "639к", "15:55", "17:25", "семинар")
            ]),
            "среда": DaySchedule("среда", [
                Subject("Начертательная геометрия", "1113л, 1111л", "8:30", "10:00", "семинар"),
                Subject("Начертательная геометрия", "216л", "10:10", "11:40", "лекция"),
                Subject("Социология", "216л", "11:50", "13:55", "лекция"),
                Subject("Физическая культура", "СК", "14:30", "16:00", "семинар")
            ]),
            "четверг": DaySchedule("четверг", [
                Subject("Иностранный язык", "211х, 305х", "10:10", "11:40", "семинар"),
                Subject("Аналитическая геометрия", "114х", "11:50", "13:55", "семинар"),
                Subject("Аналитическая геометрия", "301х", "14:05", "15:35", "лекция")
            ]),
            "пятница": DaySchedule("пятница", [
                Subject("Физкультура", "СК", "13:55", "15:30", "семинар"),
                Subject("Информатика", "601к", "15:55", "17:25", "лабораторная работа"),
                Subject("Основы программирования", "540к", "17:35", "19:05", "семинар")
            ]),
            "суббота": DaySchedule("суббота", [
                Subject("Математический анализ", "536к", "8:30", "10:00", "семинар"),
                Subject("Социология", "537к", "10:10", "11:40", "семинар"),
                Subject("Математический анализ", "532к", "12:25", "13:55", "семинар")
            ])
        }

    def _parse_denominator_schedule(self) -> Dict[str, DaySchedule]:
        """Парсинг расписания для знаменателя"""
        return {
            "понедельник": DaySchedule("понедельник", [
                Subject("Основы программирования", "301х", "14:05", "15:35", "лекция"),
                Subject("Информатика", "301х", "14:05", "15:35", "лекция")
            ]),
            "вторник": DaySchedule("вторник", [
                Subject("Математический анализ", "301х", "10:10", "11:40", "лекция"),
                Subject("Основы программирования", "524к", "12:25", "13:55", "лабораторная работа"),
                Subject("История России", "618к", "14:05", "15:35", "семинар")
            ]),
            "среда": DaySchedule("среда", [
                Subject("Начертательная геометрия", "1113л, 1111л", "8:30", "10:00", "семинар"),
                Subject("Начертательная геометрия", "216л", "10:10", "11:40", "лекция"),
                Subject("История России", "216л", "11:50", "13:55", "лекция"),
                Subject("Физическая культура", "СК", "14:30", "16:00", "семинар")
            ]),
            "четверг": DaySchedule("четверг", [
                Subject("Иностранный язык", "211х, 305х", "10:10", "11:40", "семинар"),
                Subject("Аналитическая геометрия", "114х", "11:50", "13:55", "семинар"),
                Subject("Аналитическая геометрия", "301х", "14:05", "15:35", "лекция")
            ]),
            "пятница": DaySchedule("пятница", [
                Subject("Физкультура", "СК", "13:55", "15:30", "семинар"),
                Subject("Информатика", "601к", "15:55", "17:25", "лабораторная работа"),
                Subject("Основы программирования", "540к", "17:35", "19:05", "семинар")
            ]),
            "суббота": DaySchedule("суббота", [
                Subject("Математический анализ", "536к", "8:30", "10:00", "семинар"),
                Subject("Социология", "537к", "10:10", "11:40", "семинар"),
                Subject("Математический анализ", "532к", "12:25", "13:55", "консультация")
            ])
        }
    
    def is_numerator_week(self, date: datetime = None) -> bool:
        """Определяет, является ли неделя числителем"""
        if date is None:
            date = datetime.now()
        
        delta = date - self.semester_start
        week_number = delta.days // 7
        return week_number % 2 == 0
    
    def get_day_schedule(self, date: datetime = None) -> Optional[DaySchedule]:
        """Получает расписание на указанную дату"""
        if date is None:
            date = datetime.now()
        
        days_russian = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
        day_name = days_russian[date.weekday()]
        
        if self.is_numerator_week(date):
            schedule = self.numerator_schedule
        else:
            schedule = self.denominator_schedule
        
        return schedule.get(day_name)
    
    def format_schedule_for_day(self, date: datetime = None, include_control_events: bool = True) -> str:
        """Форматирует расписание на день в красивый текст"""
        day_schedule = self.get_day_schedule(date)
        if not day_schedule:
            return "🎉 В этот день занятий нет"
        
        control_events = {}
        if include_control_events:
            date_str = date.strftime("%Y-%m-%d")
            events = db.get_control_events_by_date(date_str)
            for subject_name, event_type in events:
                control_events[subject_name] = event_type
        
        day_emojis = {
            "понедельник": "📅 Понедельник", "вторник": "📅 Вторник", "среда": "📅 Среда",
            "четверг": "📅 Четверг", "пятница": "📅 Пятница", "суббота": "📅 Суббота"
        }
        
        day_display = day_emojis.get(day_schedule.day_name, day_schedule.day_name)
        week_type = "Числитель" if self.is_numerator_week(date) else "Знаменатель"
        
        result = f"{day_display} ({week_type})\n\n"
        
        for i, subject in enumerate(day_schedule.subjects, 1):
            event_mark = ""
            if subject.name in control_events:
                event_mark = f" 🚨 {control_events[subject.name]}"
            
            result += f"🕒 {subject.start_time}-{subject.end_time}\n"
            result += f"📚 {subject.name}\n"
            result += f"🏫 {subject.room}\n"
            result += f"📝 {subject.lesson_type}{event_mark}\n"
            
            if i < len(day_schedule.subjects):
                result += "───────\n"
        
        return result
    
    def get_week_schedule(self) -> str:
        """Получает расписание на всю неделю"""
        try:
            current_date = datetime.now()
            is_numerator = self.is_numerator_week(current_date)
            week_type = "Числитель" if is_numerator else "Знаменатель"
            
            schedule = self.numerator_schedule if is_numerator else self.denominator_schedule
            days_order = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]
            
            result = f"📅 Расписание на неделю ({week_type})\n\n"
            
            for day_name in days_order:
                day_schedule = schedule.get(day_name)
                if not day_schedule or not day_schedule.subjects:
                    continue
                
                day_emojis = {
                    "понедельник": "📅 Понедельник", "вторник": "📅 Вторник", "среда": "📅 Среда",
                    "четверг": "📅 Четверг", "пятница": "📅 Пятница", "суббота": "📅 Суббота"
                }
                
                day_display = day_emojis.get(day_name, day_name)
                result += f"{day_display}:\n"
                
                from src.utils.helpers import get_date_for_weekday
                day_date = get_date_for_weekday(day_name, current_date)
                
                control_events = {}
                date_str = day_date.strftime("%Y-%m-%d")
                events = db.get_control_events_by_date(date_str)
                for subject_name, event_type in events:
                    control_events[subject_name] = event_type
                
                for i, subject in enumerate(day_schedule.subjects, 1):
                    event_mark = ""
                    if subject.name in control_events:
                        event_mark = f" 🚨 {control_events[subject.name]}"
                    
                    result += f"  {i}. {subject.name}\n"
                    result += f"     ⏰ {subject.start_time}-{subject.end_time}\n"
                    result += f"     🏫 {subject.room} ({subject.lesson_type}){event_mark}\n"
                
                result += "\n"
            
            if result == f"📅 Расписание на неделю ({week_type})\n\n":
                result = "🎉 На этой неделе занятий нет"
                
            return result
            
        except Exception as e:
            logger.error(f"Ошибка получения расписания на неделю: {e}")
            return "❌ Не удалось получить расписание на неделю"
    
    def get_tomorrow_schedule(self) -> str:
        """Получает расписание на завтра"""
        tomorrow = datetime.now() + timedelta(days=1)
        return self.format_schedule_for_day(tomorrow)
    
    def get_today_schedule(self) -> str:
        """Получает расписание на сегодня"""
        return self.format_schedule_for_day(datetime.now())
    
    def get_subjects_with_times(self, date: datetime = None) -> List[Dict]:
        """Возвращает список предметов с временами для напоминаний"""
        if date is None:
            date = datetime.now()
            
        day_schedule = self.get_day_schedule(date)
        if not day_schedule:
            return []
        
        subjects_with_times = []
        for subject in day_schedule.subjects:
            subjects_with_times.append({
                'name': subject.name,
                'start_time': subject.start_time,
                'end_time': subject.end_time,
                'room': subject.room,
                'type': subject.lesson_type
            })
        
        return subjects_with_times

# Глобальный экземпляр менеджера расписания
schedule_manager = ScheduleManager()