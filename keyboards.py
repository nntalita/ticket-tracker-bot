from telegram import ReplyKeyboardMarkup

def get_main_keyboard():
    """Основная клавиатура с кнопками"""
    keyboard = [
        ["✈️ Добавить маршрут"],
        ["📋 Мои маршруты", "💰 Проверить цены"],
        ["📊 Статистика", "❓ Помощь"],
        ["❌ Удалить маршрут"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_cancel_keyboard():
    """Клавиатура для отмены"""
    keyboard = [["❌ Отмена"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)