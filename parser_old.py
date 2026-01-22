import random
from datetime import datetime

class TicketParser:
    def check_route(self, route_text):
        price = 7500.0
        return {
            'success': True,
            'route': route_text,
            'price': price,
            'available': True,
            'currency': 'RUB',
            'checked_at': '2024-01-21'
        }

parser = TicketParser()