import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.transmission import get_client, is_connected
from utils.helpers import auth, get_torrent_progress
from config import CHAT_ID
from handlers.commands import completed_torrents

logger = logging.getLogger(__name__)


async def list_torrents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /list"""
    if not auth(update, CHAT_ID) or not is_connected():
        return
    
    tc = get_client()
    try:
        torrents = tc.get_torrents()
        if not torrents:
            await update.message.reply_text("Нет активных загрузок.")
            return

        response = "Активные загрузки:\n\n"
        for torrent in torrents:
            status = torrent.status
            progress = round(get_torrent_progress(torrent), 1)
            response += f"[ID: {torrent.id}] {torrent.name}\n"
            response += f"— Статус: {status}, Прогресс: {progress}%\n\n"
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Ошибка при получении списка торрентов: {e}")
        await update.message.reply_text(f"Ошибка: {e}")


async def add_torrent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /add"""
    if not auth(update, CHAT_ID) or not is_connected():
        return
    
    if not context.args:
        await update.message.reply_text(
            "Укажите magnet-ссылку. Пример: /add magnet:?xt=urn:btih:..."
        )
        return

    tc = get_client()
    magnet_link = context.args[0]
    try:
        logger.info(f"Добавление торрента: {magnet_link[:50]}...")
        tc.add_torrent(magnet_link)
        await update.message.reply_text("Торрент добавлен в очередь на загрузку!")
        logger.info(f"Торрент успешно добавлен пользователем {update.effective_chat.id}")
    except Exception as e:
        logger.error(f"Ошибка при добавлении торрента: {e}")
        await update.message.reply_text(f"Ошибка при добавлении торрента: {e}")


async def pause_torrent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /pause"""
    if not auth(update, CHAT_ID) or not is_connected():
        return
    
    if not context.args:
        await update.message.reply_text("Укажите ID торрента. Пример: /pause 1")
        return

    tc = get_client()
    try:
        torrent_id = int(context.args[0])
        tc.stop_torrent(torrent_id)
        await update.message.reply_text(f"Торрент #{torrent_id} приостановлен.")
    except Exception as e:
        logger.error(f"Ошибка при приостановке торрента: {e}")
        await update.message.reply_text(f"Ошибка: {e}")


async def resume_torrent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /resume"""
    if not auth(update, CHAT_ID) or not is_connected():
        return
    
    if not context.args:
        await update.message.reply_text("Укажите ID торрента. Пример: /resume 1")
        return

    tc = get_client()
    try:
        torrent_id = int(context.args[0])
        tc.start_torrent(torrent_id)
        await update.message.reply_text(f"Торрент #{torrent_id} возобновлен.")
    except Exception as e:
        logger.error(f"Ошибка при возобновлении торрента: {e}")
        await update.message.reply_text(f"Ошибка: {e}")


async def remove_torrent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /remove - удаляет торрент из списка (без удаления файлов)"""
    if not auth(update, CHAT_ID) or not is_connected():
        return
    
    if not context.args:
        await update.message.reply_text("Укажите ID торрента. Пример: /remove 1")
        return

    tc = get_client()
    try:
        torrent_id = int(context.args[0])
        tc.remove_torrent(torrent_id, delete_data=False)
        await update.message.reply_text(f"Торрент #{torrent_id} удален из списка (файлы сохранены).")
    except Exception as e:
        logger.error(f"Ошибка при удалении торрента: {e}")
        await update.message.reply_text(f"Ошибка: {e}")


async def delete_torrent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /delete - удаляет торрент с файлами"""
    if not auth(update, CHAT_ID) or not is_connected():
        return
    
    if not context.args:
        await update.message.reply_text("Укажите ID торрента. Пример: /delete 1")
        return

    tc = get_client()
    try:
        torrent_id = int(context.args[0])
        tc.remove_torrent(torrent_id, delete_data=True)
        await update.message.reply_text(f"Торрент #{torrent_id} удален вместе с файлами.")
    except Exception as e:
        logger.error(f"Ошибка при удалении торрента: {e}")
        await update.message.reply_text(f"Ошибка: {e}")


async def completed_torrents_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /completed"""
    if not auth(update, CHAT_ID):
        return

    if not completed_torrents:
        await update.message.reply_text("Нет завершенных загрузок за текущую сессию.")
    else:
        response = "Последние завершенные загрузки:\n\n"
        tc = get_client()
        for torrent_id in completed_torrents:
            try:
                if tc:
                    torrent = tc.get_torrent(torrent_id)
                    response += f"📁 {torrent.name} (ID: {torrent_id})\n"
                else:
                    response += f"📁 Торрент ID: {torrent_id}\n"
            except:
                response += f"📁 Торрент ID: {torrent_id} (информация недоступна)\n"

        await update.message.reply_text(response)

