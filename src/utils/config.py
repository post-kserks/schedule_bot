# utils/config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_USERNAMES = os.getenv('ADMIN_USERNAMES', '')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле")

def get_admin_usernames():
    """Получает список username администраторов"""
    admin_usernames = []
    
    if ADMIN_USERNAMES:
        try:
            usernames = [x.strip().lstrip('@') for x in ADMIN_USERNAMES.split(',')]
            admin_usernames.extend([username for username in usernames if username])
        except Exception as e:
            print(f"Ошибка парсинга ADMIN_USERNAMES: {e}")
    
    if ADMIN_USERNAME and ADMIN_USERNAME not in admin_usernames:
        admin_usernames.append(ADMIN_USERNAME.lstrip('@'))
    
    return admin_usernames

ADMIN_USERNAME_LIST = get_admin_usernames()

if ADMIN_USERNAME_LIST:
    print(f"Загружены username администраторов: {ADMIN_USERNAME_LIST}")
else:
    print("⚠️  Предупреждение: не заданы username администраторов")