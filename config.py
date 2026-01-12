import os

# Пытаемся загрузить dotenv, если он установлен
try:
    from dotenv import load_dotenv
    # Загружаем переменные окружения из .env файла
    load_dotenv()
except ImportError:
    # Если dotenv не установлен, используем только системные переменные окружения
    pass

# Telegram Bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = int(os.getenv('CHAT_ID', 0))

# Transmission
TRANSMISSION_HOST = os.getenv('TRANSMISSION_HOST', 'localhost')
TRANSMISSION_PORT = int(os.getenv('TRANSMISSION_PORT', 9091))
TRANSMISSION_USER = os.getenv('TRANSMISSION_USER')
TRANSMISSION_PASSWORD = os.getenv('TRANSMISSION_PASSWORD')

