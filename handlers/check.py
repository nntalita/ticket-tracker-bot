from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from database import db
from parser import parser
from keyboards import get_main_keyboard
import logging

logger = logging.getLogger(__name__)

async def check_prices_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /check"""
    return await check_prices_message(update, context)

async def check_prices_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Проверить цены'"""
    user_id = update.effective_user.id
    tracks = db.get_user_tracks(user_id)
    
    if not tracks:
        await update.message.reply_text(
            "📭 У вас нет маршрутов для проверки.\n"
            "Добавьте маршрут через кнопку ✈️ Добавить маршрут",
            reply_markup=get_main_keyboard()
        )
        return
    
    message = await update.message.reply_text(
        "🔍 Начинаю проверку цен...",
        reply_markup=get_main_keyboard()
    )
    
    found_prices = []
    
    for track in tracks:
        try:
            result = parser.check_route(track['route'])
            
            if result['success'] and result['price']:
                db.update_price(track['id'], result['price'])
                found_prices.append(
                    f"• {track['route']}: {result['price']:.2f} руб"
                )
                
        except Exception as e:
            logger.error(f"Ошибка при проверке {track['route']}: {e}")
    
    if found_prices:
        response = "✅ <b>Цены обновлены:</b>\n\n" + "\n".join(found_prices)
    else:
        response = "😔 Не удалось получить цены"
    
    await message.edit_text(
        response + f"\n\nПроверено маршрутов: {len(tracks)}",
        parse_mode='HTML'
    )

# Функция для получения обработчика кнопки "Проверить цены"
def get_check_button_handler():
    return MessageHandler(filters.Regex("^💰 Проверить цены$"), check_prices_message)