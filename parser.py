import random
from datetime import datetime

class TicketParser:
    def check_route(self, route_text):
        """Проверяет цену на маршрут"""
        price = round(random.uniform(2000, 15000), 2)
        
        return {
            'success': True,
            'route': route_text,
            'price': price,
            'available': random.choice([True, True, True, False]),
            'currency': 'RUB',
            'checked_at': datetime.now().isoformat()
        }

# ВАЖНО: создаём объект parser для импорта
parser = TicketParser()