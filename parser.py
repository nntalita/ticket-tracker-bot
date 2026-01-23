"""
Parser module for getting flight prices.
Uses real Aviasales API with fallback to mock data.
"""

import logging
from typing import Optional
from real_parser import AviasalesParser  # Импортируем из отдельного файла

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем экземпляр парсера
real_parser = AviasalesParser()

def get_price(route: str) -> Optional[float]:
    """
    Main function to get price for a route.
    Uses real Aviasales API with fallback to mock data.
    
    Args:
        route: string in format "Москва-Сочи" or "Москва - Сочи"
    
    Returns:
        Price in rubles or None
    """
    try:
        logger.info(f"🔄 Запрос цены для маршрута: {route}")
        
        # Try to get real price
        real_price = real_parser.get_simple_price(route)
        
        if real_price is not None:
            logger.info(f"✅ Получена реальная цена: {real_price} руб.")
            return real_price
        else:
            # Fallback: return mock price
            logger.warning(f"⚠️ Не удалось получить реальную цену для {route}, использую заглушку")
            return get_mock_price(route)
            
    except Exception as e:
        logger.error(f"💥 Критическая ошибка в get_price: {e}")
        # Always return mock price on error
        return get_mock_price(route)


def get_mock_price(route: str) -> float:
    """
    Mock function returning fake prices.
    Used when API fails.
    """
    route_lower = route.lower()
    
    # Simple logic for demonstration
    if "пекин" in route_lower or "beijing" in route_lower:
        return 45000.0
    elif "сочи" in route_lower:
        return 12000.0
    elif "казань" in route_lower:
        return 8000.0
    elif "париж" in route_lower or "paris" in route_lower:
        return 25000.0
    elif "лондон" in route_lower or "london" in route_lower:
        return 30000.0
    elif "дубай" in route_lower or "dubai" in route_lower:
        return 35000.0
    elif "токио" in route_lower or "tokyo" in route_lower:
        return 50000.0
    elif "санкт-петербург" in route_lower or "питер" in route_lower:
        return 7000.0
    elif "краснодар" in route_lower:
        return 9000.0
    elif "екатеринбург" in route_lower:
        return 10000.0
    elif "новосибирск" in route_lower:
        return 15000.0
    else:
        return 15000.0  # Default price


def get_available_routes() -> list:
    """
    Returns list of available routes.
    Used for bot buttons.
    """
    return [
        "Москва-Сочи",
        "Москва-Казань", 
        "Москва-Санкт-Петербург",
        "Москва-Краснодар",
        "Москва-Пекин",
        "Москва-Париж"
    ]


def format_price_message(route: str, price: float) -> str:
    """
    Formats price message for Telegram.
    """
    return f"🎫 Маршрут: {route}\n💰 Цена: {price:,.0f} руб.\n\n*Нажмите /start для возврата в меню*"

# === Обертка для совместимости со старым кодом ===
class ParserWrapper:
    """Обертка для совместимости со старым кодом бота"""
    def check_route(self, route):
        """Совместимость со старым кодом"""
        price = get_price(route)
        return {
            'success': True if price else False, 
            'price': price,
            'route': route
        }

# Создаем объект для обратной совместимости
parser = ParserWrapper()

# Test function
if __name__ == "__main__":
    test_routes = [
        "Москва-Сочи",
        "Санкт-Петербург - Пекин",
        "Москва-Париж",
        "Москва-Лондон",
        "Неизвестный-Маршрут"
    ]
    
    print("🧪 Тестирование интеграции парсера:\n")
    
    for route in test_routes:
        print(f"🔍 Маршрут: {route}")
        price = get_price(route)
        source = "РЕАЛЬНЫЙ API" if price != get_mock_price(route) else "ЗАГЛУШКА (fallback)"
        print(f"   💰 Цена: {price:,.0f} руб. ({source})")
        print()