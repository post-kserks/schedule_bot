# handlers/callback_handlers.py
import logging
from telegram import Update
from telegram.ext import ContextTypes
from src.services.admin_panel import admin_panel

logger = logging.getLogger(__name__)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Основной обработчик callback запросов"""
    query = update.callback_query
    await query.answer()
    
    # Передаем обработку в админ-панель
    await admin_panel.handle_admin_callback(update, context)