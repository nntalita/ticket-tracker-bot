from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from keyboards import get_main_keyboard

async def help_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Помощь'"""
    help_text = (
        "🎫 <b>Бот для отслеживания цен на билеты</b>\n\n"
        "✅ <b>Как пользоваться:</b>\n"
        "1. Нажмите <b>✈️ Добавить маршрут</b>\n"
        "2. Введите маршрут: <i>Город-Город</i>\n"
        "3. Нажмите <b>💰 Проверить цены</b>\n"
        "4. Бот покажет текущие цены\n\n"
        "⏰ <b>Автопроверка:</b>\n"
        "Бот проверяет цены каждый день в 10:00\n"
        "При падении цены - уведомление!\n\n"
        "📋 <b>Просмотр маршрутов:</b>\n"
        "Используйте кнопку <b>📋 Мои маршруты</b>\n\n"
        "❌ <b>Удалить маршрут:</b>\n"
        "Используйте кнопку <b>❌ Удалить маршрут</b>"
    )
    
    await update.message.reply_html(
        help_text,
        reply_markup=get_main_keyboard()
    )

async def delete_route_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Удалить маршрут'"""
    from database import db
    
    user_id = update.effective_user.id
    tracks = db.get_user_tracks(user_id)
    
    if not tracks:
        await update.message.reply_text(
            "📭 Нет маршрутов для удаления.",
            reply_markup=get_main_keyboard()
        )
        return
    
    response = "🗑️ <b>Выберите маршрут для удаления:</b>\n\n"
    
    for i, track in enumerate(tracks, 1):
        response += f"{i}. {track['route']} (ID: {track['id']})\n"
    
    response += "\n❌ Для удаления введите команду:\n"
    response += "<code>/stop номер</code>\n\n"
    response += "Например: <code>/stop 1</code>"
    
    await update.message.reply_html(
        response,
        reply_markup=get_main_keyboard()
    )

async def cancel_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Отмена'"""
    await update.message.reply_text(
        "✅ Хорошо, действие отменено.",
        reply_markup=get_main_keyboard()
    )

# Функции для получения обработчиков кнопок
def get_help_button_handler():
    return MessageHandler(filters.Regex("^❓ Помощь$"), help_message)

def get_delete_button_handler():
    return MessageHandler(filters.Regex("^❌ Удалить маршрут$"), delete_route_message)

def get_cancel_button_handler():
    return MessageHandler(filters.Regex("^❌ Отмена$"), cancel_message)