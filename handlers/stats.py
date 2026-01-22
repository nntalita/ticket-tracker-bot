from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from database import db
from keyboards import get_main_keyboard

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stats"""
    return await stats_message(update, context)

async def stats_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Статистика'"""
    user_id = update.effective_user.id
    tracks = db.get_user_tracks(user_id)
    active_count = len(tracks)
    
    response = (
        f"📊 <b>Ваша статистика</b>\n\n"
        f"👤 Пользователь: @{update.effective_user.username or 'без username'}\n"
        f"🆔 ID: {user_id}\n\n"
        f"🎫 Активных маршрутов: <b>{active_count}</b>\n\n"
        f"⏰ <b>Автопроверка:</b>\n"
        f"Цены проверяются каждый день в 10:00\n"
        f"При падении цены получите уведомление!"
    )
    
    await update.message.reply_html(
        response,
        reply_markup=get_main_keyboard()
    )

# Функция для получения обработчика кнопки "Статистика"
def get_stats_button_handler():
    return MessageHandler(filters.Regex("^📊 Статистика$"), stats_message)