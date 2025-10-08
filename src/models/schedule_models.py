# models/schedule_models.py
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
    def __init__(self, day_name: str, subjects: list):
        self.day_name = day_name
        self.subjects = subjects
    
    def __str__(self):
        result = f"{self.day_name}\n"
        for i, subject in enumerate(self.subjects, 1):
            result += f"{subject}\n"
        return result