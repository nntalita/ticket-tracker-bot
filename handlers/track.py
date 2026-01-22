from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler
from database import db
from keyboards import get_main_keyboard, get_cancel_keyboard

# Состояния для ConversationHandler
WAITING_FOR_ROUTE = 1

async def track_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /track"""
    try:
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
        
        # Проверяем, есть ли уже такой маршрут у пользователя
        existing_tracks = db.get_user_tracks(user_id)
        existing_routes = [t['route'] for t in existing_tracks]
        
        if route in existing_routes:
            await update.message.reply_html(
                f"⚠️ <b>Маршрут уже отслеживается!</b>\n\n"
                f"📍 <code>{route}</code>\n\n"
                f"Вы можете проверить цены через кнопку 💰 Проверить цены",
                reply_markup=get_main_keyboard()
            )
            return
        
        # Добавляем в базу данных
        track_id = db.add_track(user_id=user_id, route=route)
        
        response = (
            f"✅ Маршрут добавлен!\n\n"
            f"📍 <b>{route}</b>\n"
            f"🆔 ID: {track_id}\n\n"
            f"Теперь я буду следить за ценами!"
        )
        
        await update.message.reply_html(response, reply_markup=get_main_keyboard())
        
    except Exception as e:
        # Логируем ошибку
        print(f"❌ Ошибка в track_command: {e}")
        
        # Сообщаем пользователю
        await update.message.reply_text(
            "❌ Что-то пошло не так...\n"
            "Попробуйте еще раз или нажмите /start",
            reply_markup=get_main_keyboard()
        )

async def start_add_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало добавления маршрута через кнопку"""
    try:
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
    except Exception as e:
        print(f"❌ Ошибка в start_add_route: {e}")
        return ConversationHandler.END

async def process_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка введенного маршрута"""
    try:
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
        
        # Проверяем, есть ли уже такой маршрут у пользователя
        existing_tracks = db.get_user_tracks(user_id)
        existing_routes = [t['route'] for t in existing_tracks]
        
        if route in existing_routes:
            await update.message.reply_html(
                f"⚠️ <b>Маршрут уже отслеживается!</b>\n\n"
                f"📍 <code>{route}</code>\n\n"
                f"Вы можете проверить цены через кнопку 💰 Проверить цены",
                reply_markup=get_main_keyboard()
            )
            return ConversationHandler.END
        
        # Добавляем в базу данных
        track_id = db.add_track(user_id=user_id, route=route)
        
        response = (
            f"✅ <b>Маршрут добавлен!</b>\n\n"
            f"📍 {route}\n"
            f"🆔 ID: {track_id}\n\n"
            f"Теперь я буду следить за цены на этот маршрут!"
        )
        
        await update.message.reply_html(
            response,
            reply_markup=get_main_keyboard()
        )
        return ConversationHandler.END
        
    except Exception as e:
        # Логируем ошибку
        print(f"❌ Ошибка в process_route: {e}")
        
        # Сообщаем пользователю
        await update.message.reply_text(
            "❌ Что-то пошло не так...\n"
            "Попробуйте еще раз или нажмите /start",
            reply_markup=get_main_keyboard()
        )
        return ConversationHandler.END

async def cancel_add_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена добавления маршрута"""
    try:
        await update.message.reply_text(
            "❌ Добавление маршрута отменено.",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        print(f"❌ Ошибка в cancel_add_route: {e}")
    finally:
        return ConversationHandler.END

async def stop_track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stop"""
    try:
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
    except Exception as e:
        print(f"❌ Ошибка в stop_track: {e}")
        await update.message.reply_text(
            "❌ Что-то пошло не так...",
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
            # Исправленный Regex: ловит просто тмена
            MessageHandler(filters.Regex(".*тмена.*"), cancel_add_route)
        ]
    )