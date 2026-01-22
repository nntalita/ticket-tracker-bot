from typing import List, Dict, Optional
import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name: str = "ticket_bot.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        """Создаем таблицы если их нет"""
        cursor = self.conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица отслеживаемых маршрутов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                route TEXT,
                origin TEXT,
                destination TEXT,
                min_price REAL DEFAULT NULL,
                last_check TIMESTAMP DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица истории цен
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER,
                price REAL,
                found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (track_id) REFERENCES tracks (id)
            )
        ''')
        
        self.conn.commit()
    
    def add_user(self, user_id: int, username: Optional[str] = None, 
                 first_name: Optional[str] = None, last_name: Optional[str] = None):
        """Добавляем или обновляем пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, username, first_name, last_name) 
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        self.conn.commit()
    
    def add_track(self, user_id: int, route: str, 
                  origin: Optional[str] = None, destination: Optional[str] = None) -> int:
        """Добавляем маршрут для отслеживания (с проверкой дубликатов)"""
        cursor = self.conn.cursor()
        
        # Проверяем, есть ли уже такой активный маршрут у пользователя
        cursor.execute('''
            SELECT id FROM tracks 
            WHERE user_id = ? AND route = ? AND active = 1
        ''', (user_id, route))
        
        existing = cursor.fetchone()
        if existing:
            return existing[0]  # Возвращаем ID существующего маршрута
        
        # Если дубликата нет - добавляем новый
        cursor.execute('''
            INSERT INTO tracks (user_id, route, origin, destination)
            VALUES (?, ?, ?, ?)
        ''', (user_id, route, origin, destination))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_tracks(self, user_id: int) -> List[Dict]:
        """Получаем все активные маршруты пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, route, min_price, last_check, created_at
            FROM tracks 
            WHERE user_id = ? AND active = 1
            ORDER BY created_at DESC
        ''', (user_id,))
        
        tracks = []
        for row in cursor.fetchall():
            tracks.append({
                'id': row[0],
                'route': row[1],
                'min_price': row[2],
                'last_check': row[3],
                'created_at': row[4]
            })
        return tracks
    
    def update_price(self, track_id: int, price: float):
        """Обновляем минимальную цену для маршрута"""
        cursor = self.conn.cursor()
        
        # Добавляем запись в историю
        cursor.execute('''
            INSERT INTO price_history (track_id, price)
            VALUES (?, ?)
        ''', (track_id, price))
        
        # Обновляем минимальную цену в tracks
        cursor.execute('''
            UPDATE tracks 
            SET min_price = CASE 
                WHEN min_price IS NULL OR ? < min_price THEN ? 
                ELSE min_price 
            END,
            last_check = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (price, price, track_id))
        
        self.conn.commit()
    
    def deactivate_track(self, track_id: int, user_id: int):
        """Деактивируем маршрут"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE tracks 
            SET active = 0 
            WHERE id = ? AND user_id = ?
        ''', (track_id, user_id))
        self.conn.commit()
        return cursor.rowcount > 0

# Глобальный экземпляр базы данных
db = Database()