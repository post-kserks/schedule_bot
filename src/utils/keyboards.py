# utils/keyboards.py
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard():
    """Возвращает основную клавиатуру с кнопками"""
    keyboard = [
        [KeyboardButton("📅 Сегодня"), KeyboardButton("📆 Завтра")],
        [KeyboardButton("📅 Неделя"), KeyboardButton("❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard():
    """Возвращает клавиатуру для администратора"""
    keyboard = [
        [KeyboardButton("📅 Сегодня"), KeyboardButton("📆 Завтра")],
        [KeyboardButton("📅 Неделя"), KeyboardButton("❓ Помощь")],
        [KeyboardButton("⚙️ Админ-панель")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_menu_keyboard():
    """Клавиатура для админ-панели"""
    keyboard = [
        [InlineKeyboardButton("📋 Список мероприятий", callback_data="admin_list_events")],
        [InlineKeyboardButton("➕ Добавить мероприятие", callback_data="admin_add_event")],
        [InlineKeyboardButton("❌ Удалить мероприятие", callback_data="admin_delete_event")],
        [InlineKeyboardButton("📢 Сообщение всем", callback_data="admin_broadcast_message")],
        [InlineKeyboardButton("👥 Список админов", callback_data="admin_list_admins")],
        [InlineKeyboardButton("⬅️ Назад к расписанию", callback_data="admin_back_to_schedule")]
    ]
    return InlineKeyboardMarkup(keyboard)