from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from database import db
from keyboards import get_main_keyboard

async def list_tracks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /list"""
    return await list_tracks_message(update, context)

async def list_tracks_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Мои маршруты'"""
    user_id = update.effective_user.id
    tracks = db.get_user_tracks(user_id)
    
    if not tracks:
        await update.message.reply_text(
            "📭 У вас пока нет отслеживаемых маршрутов.\n"
            "Добавьте первый через кнопку ✈️ Добавить маршрут",
            reply_markup=get_main_keyboard()
        )
        return
    
    response = "📋 <b>Ваши маршруты:</b>\n\n"
    
    for i, track in enumerate(tracks, 1):
        created_date = track['created_at'][:10] if track['created_at'] else "ещё нет"
        last_check = track['last_check'][:10] if track['last_check'] else "не проверялся"
        
        if track['min_price']:
            price_info = f"💰 от {track['min_price']:.2f} руб"
        else:
            price_info = "💰 цена неизвестна"
        
        response += (
            f"{i}. <b>{track['route']}</b>\n"
            f"   🆔 ID: {track['id']} | 📅 Добавлен: {created_date}\n"
            f"   {price_info} | 🔍 Проверка: {last_check}\n\n"
        )
    
    response += f"Всего маршрутов: {len(tracks)}\n"
    response += "❌ Удалить: нажмите кнопку ❌ Удалить маршрут"
    
    await update.message.reply_html(
        response,
        reply_markup=get_main_keyboard()
    )

# Функция для получения обработчика кнопки "Мои маршруты"
def get_list_button_handler():
    return MessageHandler(filters.Regex("^📋 Мои маршруты$"), list_tracks_message)