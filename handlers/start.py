from telegram import Update
from telegram.ext import ContextTypes
from database import db
from keyboards import get_main_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Сохраняем пользователя в БД
    db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n"
        "Я бот для отслеживания цен на билеты.\n\n"
        "Используйте кнопки ниже:",
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text(
        "Используйте кнопки меню:\n"
        "✈️ Добавить маршрут - добавить новый маршрут\n"
        "📋 Мои маршруты - список ваших маршрутов\n"
        "💰 Проверить цены - проверить цены сейчас\n"
        "📊 Статистика - ваша статистика\n"
        "❌ Удалить маршрут - удалить маршрут\n"
        "❓ Помощь - эта справка",
        reply_markup=get_main_keyboard()
    )