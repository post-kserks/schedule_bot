# database.py
import sqlite3
import logging
import os
from datetime import datetime
from config import ADMIN_USERNAME

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path="schedule.db"):
        # Если путь не абсолютный, используем текущую директорию
        if not os.path.isabs(db_path):
            # В Docker используем папку data, иначе текущую директорию
            if os.path.exists('/app/data'):
                self.db_path = "/app/data/schedule.db"
            else:
                self.db_path = os.path.join(os.getcwd(), db_path)
        else:
            self.db_path = db_path
        
        # Создаем папку для БД если нужно (только если есть путь в db_path)
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Создана директория для БД: {db_dir}")
        
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Инициализация базы данных"""
        try:
            with self.get_connection() as conn:
                # Таблица для контрольных мероприятий
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS control_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        subject_name TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by TEXT DEFAULT NULL
                    )
                ''')
                
                # Таблица для пользователей
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                logger.info(f"База данных инициализирована: {self.db_path}")
        except Exception as e:
            logger.error(f"Ошибка инициализации БД: {e}")
            raise
    
    def add_control_event(self, date, subject_name, event_type, created_by=None):
        """Добавление контрольного мероприятия"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    INSERT INTO control_events (date, subject_name, event_type, created_by)
                    VALUES (?, ?, ?, ?)
                ''', (date, subject_name, event_type, created_by))
                conn.commit()
                logger.info(f"Добавлено контрольное мероприятие: {subject_name} на {date}")
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Ошибка добавления контрольного мероприятия: {e}")
            return None
    
    def get_control_events_by_date(self, date):
        """Получение контрольных мероприятий на указанную дату"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT subject_name, event_type 
                    FROM control_events 
                    WHERE date = ?
                ''', (date,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка получения контрольных мероприятий: {e}")
            return []
    
    def delete_control_event(self, event_id):
        """Удаление контрольного мероприятия"""
        try:
            with self.get_connection() as conn:
                conn.execute('DELETE FROM control_events WHERE id = ?', (event_id,))
                conn.commit()
                logger.info(f"Удалено контрольное мероприятие ID: {event_id}")
                return True
        except Exception as e:
            logger.error(f"Ошибка удаления контрольного мероприятия: {e}")
            return False
    
    def get_all_control_events(self):
        """Получение всех контрольных мероприятий (для админа)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT id, date, subject_name, event_type, created_by
                    FROM control_events 
                    ORDER BY date
                ''')
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка получения всех контрольных мероприятий: {e}")
            return []

    def add_user(self, user_id: int, username: str, first_name: str, last_name: str = None):
        """Добавление/обновление пользователя"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name) 
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name))
                conn.commit()
                logger.info(f"Добавлен/обновлен пользователь: {username}")
                return True
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя: {e}")
            return False
    
    def get_all_users(self):
        """Получение всех пользователей"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('SELECT user_id FROM users')
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Ошибка получения пользователей: {e}")
            return []
    
    def user_exists(self, user_id: int):
        """Проверка существования пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Ошибка проверки пользователя: {e}")
            return False

# Глобальный экземпляр базы данных
db = Database()