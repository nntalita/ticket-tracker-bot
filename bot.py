#!/usr/bin/env python3
"""
Главный файл бота для отслеживания цен на билеты
Модульная структура проекта
"""

import logging
from datetime import datetime
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Импорты из наших модулей
from database import db
from parser import parser
from keyboards import get_main_keyboard
from utils.logger import setup_logger, setup_cleanup

# Импорты обработчиков команд
from handlers.start import start, help_command
from handlers.track import track_command, stop_track, get_track_conversation_handler
from handlers.list import list_tracks_command
from handlers.check import check_prices_command
from handlers.stats import stats_command
from handlers.common import (
    get_help_button_handler,
    get_delete_button_handler,
    get_cancel_button_handler
)

# Импорты обработчиков кнопок
from handlers.list import get_list_button_handler
from handlers.check import get_check_button_handler
from handlers.stats import get_stats_button_handler

# Обработчики кнопок (общие)
from handlers.common import help_message, delete_route_message, cancel_message

async def daily_check(context):
    """Автоматическая проверка цен раз в день"""
    logger = logging.getLogger(__name__)
    logger.info("🔍 Запуск ежедневной проверки цен...")
    
    try:
        cursor = db.conn.cursor()
        cursor.execute('SELECT DISTINCT user_id FROM tracks WHERE active = 1')
        users = cursor.fetchall()
        
        checked_users = 0
        
        for (user_id,) in users:
            try:
                tracks = db.get_user_tracks(user_id)
                
                for track in tracks:
                    try:
                        result = parser.check_route(track['route'])
                        
                        if result['success'] and result['price']:
                            old_price = track['min_price']
                            new_price = result['price']
                            db.update_price(track['id'], new_price)
                            
                            if old_price and new_price < old_price:
                                message = (
                                    f"🎉 Цена упала!\n\n"
                                    f"📍 {track['route']}\n"
                                    f"📉 Было: {old_price:.2f} руб\n"
                                    f"📊 Стало: {new_price:.2f} руб\n"
                                    f"💰 Экономия: {old_price - new_price:.2f} руб"
                                )
                                
                                try:
                                    await context.bot.send_message(
                                        chat_id=user_id,
                                        text=message,
                                        reply_markup=get_main_keyboard()
                                    )
                                except:
                                    logger.warning(f"Не удалось отправить сообщение пользователю {user_id}")
                                    
                    except Exception as e:
                        logger.error(f"Ошибка при проверке {track['route']}: {e}")
                
                checked_users += 1
                    
            except Exception as e:
                logger.error(f"Ошибка для пользователя {user_id}: {e}")
        
        logger.info(f"✅ Ежедневная проверка завершена. Проверено пользователей: {checked_users}")
        
    except Exception as e:
        logger.error(f"Ошибка в daily_check: {e}")

def register_handlers(application):
    """Регистрация всех обработчиков команд и кнопок"""
    
    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("track", track_command))
    application.add_handler(CommandHandler("list", list_tracks_command))
    application.add_handler(CommandHandler("stop", stop_track))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("check", check_prices_command))
    
    # ConversationHandler для добавления маршрута через кнопку
    application.add_handler(get_track_conversation_handler())
    
    # Обработчики кнопок
    application.add_handler(get_list_button_handler())      # 📋 Мои маршруты
    application.add_handler(get_check_button_handler())     # 💰 Проверить цены
    application.add_handler(get_stats_button_handler())     # 📊 Статистика
    application.add_handler(get_help_button_handler())      # ❓ Помощь
    application.add_handler(get_delete_button_handler())    # ❌ Удалить маршрут
    application.add_handler(get_cancel_button_handler())    # ❌ Отмена

def main():
    """Главная функция запуска бота"""
    print("=" * 50)
    print("🚀 ЗАПУСК БОТА С МОДУЛЬНОЙ СТРУКТУРОЙ")
    print("=" * 50)
    
    try:
        from config import TELEGRAM_TOKEN
        
        if TELEGRAM_TOKEN == "ВАШ_ТОКЕН_ЗДЕСЬ":
            print("❌ ОШИБКА: Замените TELEGRAM_TOKEN в config.py!")
            return
        
        print("✅ База данных инициализирована")
        print("🤖 Создаю приложение...")
        
        # Создаем приложение
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Регистрируем все обработчики
        register_handlers(application)
        
        # Добавляем ежедневную проверку
        job_queue = application.job_queue
        if job_queue:
            job_queue.run_daily(
                daily_check,
                time=datetime.strptime("10:00", "%H:%M").time(),
                days=(0, 1, 2, 3, 4, 5, 6)
            )
            print("✅ Автопроверка настроена (каждый день в 10:00)")
        
        print("✅ Все обработчики зарегистрированы")
        print("=" * 50)
        print("✅ БОТ УСПЕШНО ЗАПУЩЕН!")
        print("👉 Откройте Telegram и напишите боту /start")
        print("=" * 50)
        
        # Запускаем бота
        application.run_polling()
        
    except ImportError as e:
        print(f"❌ ОШИБКА ИМПОРТА: {e}")
        print("Проверьте, что все файлы созданы правильно")
    except Exception as e:
        print(f"❌ ОШИБКА ПРИ ЗАПУСКЕ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()