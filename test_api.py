import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("AVIASALES_API_KEY")
print(f"API key loaded: {api_key[:10]}...")  # Показываем только первые 10 символов