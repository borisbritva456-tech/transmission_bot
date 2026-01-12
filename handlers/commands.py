import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.helpers import auth
from config import CHAT_ID

logger = logging.getLogger(__name__)

# Словарь для отслеживания завершенных торрентов
completed_torrents = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    if not auth(update, CHAT_ID):
        logger.warning(f"Попытка доступа от неавторизованного пользователя: {update.effective_chat.id}")
        return
    logger.info(f"Команда /start от пользователя {update.effective_chat.id}")
    await update.message.reply_text(
        'Привет! Я бот для управления Transmission. Используй /help для списка команд.'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    if not auth(update, CHAT_ID):
        return
    help_text = """
Доступные команды:
/list - Показать активные загрузки
/add <magnet_link> - Добавить торрент по magnet-ссылке
/pause <id> - Приостановить торрент по ID
/resume <id> - Возобновить торрент по ID
/remove <id> - Удалить торрент по ID (только из списка)
/delete <id> - Удалить торрент по ID с файлами
/completed - Показать последние завершенные загрузки
"""
    await update.message.reply_text(help_text)

