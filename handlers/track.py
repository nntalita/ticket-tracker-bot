from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler
from database import db
from keyboards import get_main_keyboard, get_cancel_keyboard

# Состояния для ConversationHandler
WAITING_FOR_ROUTE = 1

async def track_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /track"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "Укажите маршрут. Пример:\n"
            "<code>/track Москва-Сочи</code>\n"
            "<code>/track Санкт-Петербург-Казань</code>",
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
        return
    
    route = ' '.join(context.args)
    
    # Добавляем в базу данных
    track_id = db.add_track(user_id=user_id, route=route)
    
    response = (
        f"✅ Маршрут добавлен!\n\n"
        f"📍 <b>{route}</b>\n"
        f"🆔 ID: {track_id}\n\n"
        f"Теперь я буду следить за ценами!"
    )
    
    await update.message.reply_html(response, reply_markup=get_main_keyboard())

async def start_add_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало добавления маршрута через кнопку"""
    await update.message.reply_text(
        "✈️ <b>Введите маршрут:</b>\n\n"
        "Формат: <i>Город-Город</i>\n\n"
        "Примеры:\n"
        "• Москва-Сочи\n"
        "• Санкт-Петербург-Казань\n"
        "• Нижний Новгород-Москва\n\n"
        "Или нажмите ❌ Отмена",
        parse_mode='HTML',
        reply_markup=get_cancel_keyboard()
    )
    return WAITING_FOR_ROUTE

async def process_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка введенного маршрута"""
    user_id = update.effective_user.id
    route = update.message.text.strip()
    
    if not route or '-' not in route:
        await update.message.reply_text(
            "❌ Неверный формат маршрута!\n\n"
            "Правильный формат: <i>Город-Город</i>\n"
            "Пример: <code>Москва-Сочи</code>\n\n"
            "Попробуйте еще раз:",
            parse_mode='HTML',
            reply_markup=get_cancel_keyboard()
        )
        return WAITING_FOR_ROUTE
    
    # Добавляем в базу данных
    track_id = db.add_track(user_id=user_id, route=route)
    
    response = (
        f"✅ <b>Маршрут добавлен!</b>\n\n"
        f"📍 {route}\n"
        f"🆔 ID: {track_id}\n\n"
        f"Теперь я буду следить за ценами на этот маршрут!"
    )
    
    await update.message.reply_html(
        response,
        reply_markup=get_main_keyboard()
    )
    return ConversationHandler.END

async def cancel_add_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена добавления маршрута"""
    await update.message.reply_text(
        "❌ Добавление маршрута отменено.",
        reply_markup=get_main_keyboard()
    )
    return ConversationHandler.END

async def stop_track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stop"""
    user_id = update.effective_user.id
    
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "Укажите ID маршрута:\n"
            "<code>/stop 1</code>\n\n"
            "ID можно узнать через кнопку 📋 Мои маршруты",
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
        return
    
    track_id = int(context.args[0])
    success = db.deactivate_track(track_id, user_id)
    
    if success:
        await update.message.reply_html(
            f"✅ Маршрут #{track_id} удалён!",
            reply_markup=get_main_keyboard()
        )
    else:
        await update.message.reply_html(
            f"❌ Не удалось найти маршрут #{track_id}",
            reply_markup=get_main_keyboard()
        )

def get_track_conversation_handler():
    """Создает ConversationHandler для добавления маршрута"""
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^✈️ Добавить маршрут$"), start_add_route)],
        states={
            WAITING_FOR_ROUTE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_route)
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_add_route),
            MessageHandler(filters.Regex("^❌ Отмена$"), cancel_add_route)
        ]
    )