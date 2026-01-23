import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AVIASALES_API_KEY")
BASE_URL = "https://api.travelpayouts.com/v2/prices/latest"

def test_moscow_beijing():
    """Тест API для маршрута Москва-Пекин"""
    
    # Параметры запроса
    params = {
        "currency": "rub",       # Валюта - рубли
        "origin": "MOW",         # Москва
        "destination": "PEK",    # Пекин (IATA код)
        "token": API_KEY,
        "limit": 5               # Ограничим 5 результатами
    }
    
    print("🔄 Запрос: Москва (MOW) → Пекин (PEK)")
    print(f"🔑 API ключ: {API_KEY[:10]}...")
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=15)
        print(f"📡 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                print("✅ API запрос успешен!")
                print(f"📊 Всего найдено билетов: {len(data.get('data', []))}")
                
                # Выведем все найденные билеты
                for i, ticket in enumerate(data.get("data", [])[:5], 1):
                    print(f"\n🎫 Билет #{i}:")
                    print(f"   💰 Цена: {ticket.get('value', 'N/A')} руб.")
                    print(f"   ✈️ Авиакомпания: {ticket.get('airline', 'N/A')}")
                    print(f"   📅 Дата вылета: {ticket.get('depart_date', 'N/A')}")
                    print(f"   🔁 Пересадок: {ticket.get('transfers', 'N/A')}")
                    print(f"   🕐 В пути: {ticket.get('duration', 'N/A')} мин.")
                    
            else:
                print(f"❌ Ошибка в ответе API: {data}")
                
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            if response.text:
                print(f"Текст ошибки: {response.text[:300]}")
                
    except requests.exceptions.Timeout:
        print("⏰ Таймаут запроса (более 15 секунд)")
    except requests.exceptions.ConnectionError:
        print("🔌 Ошибка подключения к интернету")
    except Exception as e:
        print(f"💥 Неожиданная ошибка: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_moscow_beijing()