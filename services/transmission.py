import logging
import transmission_rpc as transmissionrpc
from config import TRANSMISSION_HOST, TRANSMISSION_PORT, TRANSMISSION_USER, TRANSMISSION_PASSWORD

logger = logging.getLogger(__name__)

# Инициализация клиента Transmission
try:
    if TRANSMISSION_USER and TRANSMISSION_PASSWORD:
        tc = transmissionrpc.Client(
            host=TRANSMISSION_HOST,
            port=TRANSMISSION_PORT,
            user=TRANSMISSION_USER,
            password=TRANSMISSION_PASSWORD
        )
    else:
        tc = transmissionrpc.Client(host=TRANSMISSION_HOST, port=TRANSMISSION_PORT)
except Exception as e:
    logger.error(f"Не удалось подключиться к Transmission: {e}")
    tc = None


def get_client():
    """Получить клиент Transmission"""
    return tc


def is_connected():
    """Проверить подключение к Transmission"""
    return tc is not None

