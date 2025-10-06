# schedule.py
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from database import db

logger = logging.getLogger(__name__)

class Subject:
    """Класс для представления одного занятия"""
    def __init__(self, name: str, room: str, start_time: str, end_time: str, lesson_type: str):
        self.name = name
        self.room = room
        self.start_time = start_time
        self.end_time = end_time
        self.lesson_type = lesson_type
    
    def __str__(self):
        return f"{self.name} {self.room} {self.start_time} - {self.end_time} ({self.lesson_type})"

class DaySchedule:
    """Класс для представления расписания на один день"""
    def __init__(self, day_name: str, subjects: List[Subject]):
        self.day_name = day_name
        self.subjects = subjects
    
    def __str__(self):
        result = f"{self.day_name}\n"
        for i, subject in enumerate(self.subjects, 1):
            result += f"{subject}\n"
        return result

class ScheduleManager:
    """Менеджер расписания"""
    
    def __init__(self):
        # Расписание для числителя
        self.numerator_schedule = self._parse_numerator_schedule()
        # Расписание для знаменателя
        self.denominator_schedule = self._parse_denominator_schedule()
        # Дата начала семестра для расчета недель
        self.semester_start = datetime(2024, 9, 1)  # Измените на реальную дату
    
    def _parse_numerator_schedule(self) -> Dict[str, DaySchedule]:
        """Парсинг расписания для числителя"""
        return {
            "понедельник": DaySchedule("понедельник", [
                Subject("практика иу5", "903", "10:10", "11:40", "семинар"),
                Subject("практика иу5", "903", "11:50", "13:55", "семинар"),
                Subject("основы программирования", "301х", "14:05", "15:35", "лекция"),
                Subject("основы программирования", "301х", "14:05", "15:35", "лекция")
            ]),
            "вторник": DaySchedule("вторник", [
                Subject("математический анализ", "301х", "10:10", "11:40", "лекция"),
                Subject("основы программирования", "524к", "12:25", "13:55", "лабораторная работа"),
                Subject("история России", "618к", "14:05", "15:35", "семинар"),
                Subject("информатика", "639к", "15:55", "17:25", "семинар")
            ]),
            "среда": DaySchedule("среда", [
                Subject("начертательная геометрия", "1113л, 1111л", "8:30", "10:00", "семинар"),
                Subject("начертательная геометрия", "216л", "10:10", "11:40", "лекция"),
                Subject("социология", "216л", "11:50", "13:55", "лекция"),
                Subject("физическая культура", "СК", "14:30", "16:00", "семинар")
            ]),
            "четверг": DaySchedule("четверг", [
                Subject("иностранный язык", "211х, 305х", "10:10", "11:40", "семинар"),
                Subject("аналитическая геометрия", "114х", "11:50", "13:55", "семинар"),
                Subject("аналитическая геометрия", "301х", "14:05", "15:35", "лекция")
            ]),
            "пятница": DaySchedule("пятница", [
                Subject("физкультура", "СК", "13:55", "15:30", "семинар"),
                Subject("информатика", "601к", "15:55", "17:25", "лабораторная работа"),
                Subject("основы программирования", "540к", "17:35", "19:05", "семинар")
            ]),
            "суббота": DaySchedule("суббота", [
                Subject("математический анализ", "536к", "8:30", "10:00", "семинар"),
                Subject("социология", "537к", "10:10", "11:40", "семинар"),
                Subject("математический анализ", "532к", "12:25", "13:55", "семинар")
            ])
        }
    
    def _parse_denominator_schedule(self) -> Dict[str, DaySchedule]:
        """Парсинг расписания для знаменателя"""
        return {
            "понедельник": DaySchedule("понедельник", [
                Subject("основы программирования", "301х", "14:05", "15:35", "лекция"),
                Subject("информатика", "301х", "14:05", "15:35", "лекция")
            ]),
            "вторник": DaySchedule("вторник", [
                Subject("математический анализ", "301х", "10:10", "11:40", "лекция"),
                Subject("основы программирования", "524к", "12:25", "13:55", "лабораторная работа"),
                Subject("история России", "618к", "14:05", "15:35", "семинар")
            ]),
            "среда": DaySchedule("среда", [
                Subject("начертательная геометрия", "1113л, 1111л", "8:30", "10:00", "семинар"),
                Subject("начертательная геометрия", "216л", "10:10", "11:40", "лекция"),
                Subject("история России", "216л", "11:50", "13:55", "лекция"),
                Subject("физическая культура", "СК", "14:30", "16:00", "семинар")
            ]),
            "четверг": DaySchedule("четверг", [
                Subject("иностранный язык", "211х, 305х", "10:10", "11:40", "семинар"),
                Subject("аналитическая геометрия", "114х", "11:50", "13:55", "семинар"),
                Subject("аналитическая геометрия", "301х", "14:05", "15:35", "лекция")
            ]),
            "пятница": DaySchedule("пятница", [
                Subject("физкультура", "СК", "13:55", "15:30", "семинар"),
                Subject("информатика", "601к", "15:55", "17:25", "лабораторная работа"),
                Subject("основы программирования", "540к", "17:35", "19:05", "семинар")
            ]),
            "суббота": DaySchedule("суббота", [
                Subject("математический анализ", "536к", "8:30", "10:00", "семинар"),
                Subject("социология", "537к", "10:10", "11:40", "семинар"),
                Subject("математический анализ", "532к", "12:25", "13:55", "консультация")
            ])
        }
    
    def is_numerator_week(self, date: datetime = None) -> bool:
        """Определяет, является ли неделя числителем"""
        if date is None:
            date = datetime.now()
        
        # Расчет номера недели от начала семестра
        delta = date - self.semester_start
        week_number = delta.days // 7
        
        # Четные недели - числитель, нечетные - знаменатель (или наоборот)
        # Настройте эту логику под ваше расписание
        return week_number % 2 == 0
    
    def get_day_schedule(self, date: datetime = None) -> Optional[DaySchedule]:
        """Получает расписание на указанную дату"""
        if date is None:
            date = datetime.now()
        
        # Русские названия дней недели
        days_russian = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
        day_name = days_russian[date.weekday()]
        
        # Выбор расписания в зависимости от типа недели
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
        
        # Получаем контрольные мероприятия на эту дату
        control_events = {}
        if include_control_events:
            date_str = date.strftime("%Y-%m-%d")
            events = db.get_control_events_by_date(date_str)
            for subject_name, event_type in events:
                control_events[subject_name] = event_type
        
        # Русские названия дней с эмодзи
        day_emojis = {
            "понедельник": "📅 Понедельник",
            "вторник": "📅 Вторник", 
            "среда": "📅 Среда",
            "четверг": "📅 Четверг",
            "пятница": "📅 Пятница",
            "суббота": "📅 Суббота"
        }
        
        day_display = day_emojis.get(day_schedule.day_name, day_schedule.day_name)
        
        # Добавляем информацию о типе недели
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
            # Определяем текущую дату и тип недели
            current_date = datetime.now()
            is_numerator = self.is_numerator_week(current_date)
            week_type = "Числитель" if is_numerator else "Знаменатель"
            
            # Выбираем расписание в зависимости от типа недели
            schedule = self.numerator_schedule if is_numerator else self.denominator_schedule
            
            # Порядок дней недели
            days_order = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]
            
            result = f"📅 Расписание на неделю ({week_type})\n\n"
            
            for day_name in days_order:
                day_schedule = schedule.get(day_name)
                if not day_schedule or not day_schedule.subjects:
                    continue
                
                # Русские названия дней с эмодзи
                day_emojis = {
                    "понедельник": "📅 Понедельник",
                    "вторник": "📅 Вторник", 
                    "среда": "📅 Среда",
                    "четверг": "📅 Четверг",
                    "пятница": "📅 Пятница",
                    "суббота": "📅 Суббота"
                }
                
                day_display = day_emojis.get(day_name, day_name)
                result += f"{day_display}:\n"
                
                # Получаем дату для этого дня недели
                day_date = self._get_date_for_weekday(day_name, current_date)
                
                # Получаем контрольные мероприятия на эту дату
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
    
    def _get_date_for_weekday(self, weekday: str, reference_date: datetime) -> datetime:
        """Получает дату для указанного дня недели"""
        # Сопоставление русских названий дней с индексами
        weekday_indices = {
            "понедельник": 0,
            "вторник": 1,
            "среда": 2,
            "четверг": 3,
            "пятница": 4,
            "суббота": 5,
            "воскресенье": 6
        }
        
        target_index = weekday_indices.get(weekday, 0)
        current_index = reference_date.weekday()
        
        # Вычисляем разницу в днях
        days_difference = target_index - current_index
        if days_difference < 0:
            days_difference += 7
            
        return reference_date + timedelta(days=days_difference)
    
    def get_tomorrow_schedule(self) -> str:
        """Получает расписание на завтра"""
        tomorrow = datetime.now() + timedelta(days=1)
        return self.format_schedule_for_day(tomorrow)
    
    def get_today_schedule(self) -> str:
        """Получает расписание на сегодня"""
        return self.format_schedule_for_day(datetime.now())
    
    def get_subjects_with_times(self, date: datetime = None) -> List[Dict]:
        """Возвращает список предметов с временами для напоминаний"""
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