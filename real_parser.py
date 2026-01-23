import os
import requests
import logging
from typing import Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AviasalesParser:
    """Парсер для работы с API Aviasales/Travelpayouts"""
    
    def __init__(self):
        self.api_key = os.getenv("AVIASALES_API_KEY")
        self.base_url = "https://api.travelpayouts.com/v2/prices/latest"
        
        # Словарь для конвертации городов в IATA коды
        self.city_to_iata = {
            "москва": "MOW",
            "сочи": "AER", 
            "санкт-петербург": "LED",
            "питер": "LED",
            "казань": "KZN",
            "екатеринбург": "SVX",
            "новосибирск": "OVB",
            "краснодар": "KRR",
            "пекин": "PEK",
            "париж": "CDG",
            "лондон": "LHR",
            "токио": "NRT",
            "дубай": "DXB"
        }
    
    def _get_iata_code(self, city_name: str) -> Optional[str]:
        """Конвертирует название города в IATA код"""
        city_lower = city_name.strip().lower()
        return self.city_to_iata.get(city_lower)
    
    def _get_nearest_friday(self) -> str:
        """Возвращает дату ближайшей пятницы в формате YYYY-MM-DD"""
        today = datetime.now()
        # 4 = пятница (понедельник=0)
        days_ahead = (4 - today.weekday()) % 7
        if days_ahead == 0:  # Если сегодня пятница
            days_ahead = 7
        next_friday = today + timedelta(days=days_ahead)
        return next_friday.strftime("%Y-%m-%d")
    
    def get_price(self, origin_city: str, destination_city: str) -> Optional[float]:
        """
        Получает минимальную цену на маршруте
        
        Args:
            origin_city: город отправления (например, "Москва")
            destination_city: город назначения (например, "Сочи")
        
        Returns:
            Минимальная цена в рублях или None при ошибке
        """
        try:
            # Конвертируем города в IATA коды
            origin_iata = self._get_iata_code(origin_city)
            dest_iata = self._get_iata_code(destination_city)
            
            if not origin_iata:
                logger.error(f"Не найден IATA код для города: {origin_city}")
                return None
            if not dest_iata:
                logger.error(f"Не найден IATA код для города: {destination_city}")
                return None
            
            # Параметры запроса
            params = {
                "currency": "rub",
                "origin": origin_iata,
                "destination": dest_iata,
                "token": self.api_key,
                "limit": 10  # Берем до 10 результатов
            }
            
            logger.info(f"Запрос к API: {origin_iata} → {dest_iata}")
            
            # Отправляем запрос
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()  # Проверка на HTTP ошибки
            
            data = response.json()
            
            if not data.get("success"):
                logger.error(f"API вернул ошибку: {data}")
                return None
            
            # Ищем минимальную цену среди всех билетов
            tickets = data.get("data", [])
            if not tickets:
                logger.info(f"Нет данных по маршруту {origin_iata} → {dest_iata}")
                return None
            
            # Фильтруем только билеты с ценой
            prices = [t.get("value") for t in tickets if t.get("value") is not None]
            if not prices:
                return None
            
            min_price = min(prices)
            logger.info(f"Найдена минимальная цена: {min_price} руб.")
            
            return min_price
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка сети: {e}")
            return None
        except ValueError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            return None
    
    def get_simple_price(self, route: str) -> Optional[float]:
        """
        Упрощенный интерфейс: принимает строку "Москва-Сочи" или "Москва – Сочи"
        Обрабатывает разные форматы тире для совместимости с ботом
        """
        try:
            # Очищаем строку
            route = route.strip()
            
            # Логируем что получили
            logger.debug(f"Обрабатываем маршрут: '{route}'")
            
            # Список разделителей в порядке приоритета
            separators = [" – ", " — ", " - ", "–", "—", "-"]
            
            # Пробуем каждый разделитель
            for sep in separators:
                if sep in route:
                    parts = route.split(sep)
                    if len(parts) == 2:
                        origin = parts[0].strip()
                        destination = parts[1].strip()
                        logger.debug(f"Разделитель '{sep}': '{origin}' -> '{destination}'")
                        return self.get_price(origin, destination)
            
            # Если не нашли стандартные разделители, ищем последний дефис
            # (для случаев типа "Санкт-Петербург-Пекин")
            if "-" in route:
                # Проверяем, есть ли город с дефисом
                if "санкт-петербург" in route.lower():
                    # Берем "Санкт-Петербург" как город отправления
                    origin = "Санкт-Петербург"
                    # Все что после "Санкт-Петербург-" — город назначения
                    start_idx = route.lower().find("санкт-петербург") + len("Санкт-Петербург")
                    destination = route[start_idx:].strip("- ")
                    logger.debug(f"Город с дефисом: '{origin}' -> '{destination}'")
                    return self.get_price(origin, destination)
                else:
                    # Разделяем по последнему дефису
                    last_dash = route.rfind("-")
                    if last_dash > 0:
                        origin = route[:last_dash].strip()
                        destination = route[last_dash + 1:].strip()
                        logger.debug(f"Последний дефис: '{origin}' -> '{destination}'")
                        return self.get_price(origin, destination)
            
            logger.error(f"Не удалось распарсить маршрут: '{route}'")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка в get_simple_price: {e}")
            return None


# Функция для быстрого тестирования
def test_parser():
    """Тестируем парсер на форматах из бота"""
    parser = AviasalesParser()
    
    # Форматы, которые использует бот
    test_routes = [
        "Москва–Сочи",           # Длинное тире (как в боте)
        "Санкт-Петербург – Пекин", # Тире с пробелами
        "Москва-Париж",          # Короткое тире
        "Казань — Сочи",         # Другое тире
    ]
    
    print("🧪 Тестирование форматов бота:\n")
    
    for route in test_routes:
        print(f"🔍 Маршрут: '{route}'")
        price = parser.get_simple_price(route)
        if price:
            print(f"   ✅ Цена: {price} руб.")
        else:
            print("   ❌ Не удалось получить цену")
        print()


if __name__ == "__main__":
    test_parser()