import logging
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import NetworkError, Conflict, TelegramError
from config import BOT_TOKEN, CHAT_ID
from services.transmission import is_connected, get_client
from handlers.commands import start, help_command, completed_torrents
from handlers.torrents import (
    list_torrents,
    add_torrent,
    pause_torrent,
    resume_torrent,
    remove_torrent,
    delete_torrent,
    completed_torrents_command
)
from utils.helpers import get_torrent_progress
from utils.logging_config import setup_logging

# Настройка логирования с ротацией и очисткой старых логов
setup_logging(log_dir='logs', log_level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_completed_torrents(context: ContextTypes.DEFAULT_TYPE):
    """Периодическая проверка завершенных загрузок"""
    if not is_connected():
        return

    from handlers.commands import completed_torrents

    tc = get_client()
    try:
        torrents = tc.get_torrents()
        for torrent in torrents:
            torrent_id = torrent.id
            torrent_name = torrent.name
            progress = round(get_torrent_progress(torrent), 1)

            # Если торрент завершен и мы еще не уведомляли о нем
            if progress == 100 and torrent_id not in completed_torrents:
                completed_torrents[torrent_id] = True
                size_gb = torrent.totalSize / (1024 * 1024 * 1024)
                message = (
                    f"✅ Загрузка завершена!\n\n"
                    f"📁 {torrent_name}\n"
                    f"🆔 ID: {torrent_id}\n"
                    f"💾 Размер: {size_gb:.2f} GB"
                )

                # Отправляем уведомление
                await context.bot.send_message(chat_id=CHAT_ID, text=message)
                logger.info(f"Уведомление отправлено о завершении торрента: {torrent_name}")

            # Если торрент удален или больше не завершен, удаляем из отслеживания
            elif torrent_id in completed_torrents and progress < 100:
                del completed_torrents[torrent_id]

    except Exception as e:
        logger.error(f"Ошибка при проверке завершенных торрентов: {e}")


async def cleanup_logs_job(context: ContextTypes.DEFAULT_TYPE):
    """Периодическая очистка старых логов"""
    from utils.logging_config import cleanup_old_logs
    cleanup_old_logs('logs', days=30)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок для telegram.ext.Application"""
    # Логируем ошибку
    error = context.error
    
    # Обработка NetworkError (временные проблемы сети/Telegram API)
    if isinstance(error, NetworkError):
        logger.warning(f"Network error occurred: {error}. This is usually temporary and will be retried automatically.")
        return
    
    # Обработка Conflict (запущено несколько экземпляров бота)
    if isinstance(error, Conflict):
        logger.critical(
            f"Conflict error: {error}\n"
            "This usually means multiple bot instances are running.\n"
            "Make sure only one instance is active (check systemd service and manual runs)."
        )
        return
    
    # Обработка других ошибок Telegram
    if isinstance(error, TelegramError):
        logger.error(f"Telegram error occurred: {error}", exc_info=error)
        return
    
    # Обработка всех остальных ошибок
    logger.error(
        f"Exception while handling an update: {error}",
        exc_info=error
    )


def main():
    """Главная функция запуска бота"""
    # Проверяем наличие токена
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен! Проверьте файл .env")
        return

    if not CHAT_ID:
        logger.error("CHAT_ID не установлен! Проверьте файл .env")
        return

    # Создаем Application и передаем ему токен
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_torrents))
    application.add_handler(CommandHandler("add", add_torrent))
    application.add_handler(CommandHandler("pause", pause_torrent))
    application.add_handler(CommandHandler("resume", resume_torrent))
    application.add_handler(CommandHandler("remove", remove_torrent))
    application.add_handler(CommandHandler("delete", delete_torrent))
    application.add_handler(CommandHandler("completed", completed_torrents_command))

    # Добавляем периодическую проверку завершенных торрентов
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_repeating(check_completed_torrents, interval=30, first=10)
        # Очистка старых логов раз в день (через 1 час после запуска)
        job_queue.run_repeating(
            cleanup_logs_job,
            interval=86400,  # 24 часа
            first=3600  # Через 1 час после запуска
        )

    # Запускаем бота в режиме Long Polling
    logger.info("Бот запущен...")
    logger.info("Отслеживание завершенных загрузок активно (проверка каждые 30 секунд)")
    if not is_connected():
        logger.warning("Не удалось подключиться к Transmission! Проверьте настройки.")
    
    application.run_polling()


if __name__ == '__main__':
    main()

