import logging
import atexit

def setup_logger():
    """Настройка логирования"""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    return logging.getLogger(__name__)

def setup_cleanup(db):
    """Настройка очистки при выходе"""
    def cleanup():
        try:
            db.conn.close()
            print("✅ База данных закрыта корректно")
        except:
            pass
    
    atexit.register(cleanup)