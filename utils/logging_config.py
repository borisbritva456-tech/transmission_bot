import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timedelta
from pathlib import Path


def setup_logging(log_dir='logs', log_level=logging.INFO):
    """
    Настройка логирования с ротацией файлов и очисткой старых логов
    
    Args:
        log_dir: Директория для хранения логов
        log_level: Уровень логирования
    """
    # Создаем директорию для логов, если её нет
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Формат логов
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Настройка root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Удаляем существующие обработчики, чтобы избежать дублирования
    root_logger.handlers.clear()
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(log_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Обработчик для файла с ротацией (ежедневная ротация)
    log_file = log_path / 'transmission_bot.log'
    file_handler = TimedRotatingFileHandler(
        filename=str(log_file),
        when='midnight',
        interval=1,
        backupCount=30,  # Храним 30 дней логов
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(log_format, datefmt=date_format)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Обработчик для ошибок (отдельный файл)
    error_log_file = log_path / 'errors.log'
    error_handler = TimedRotatingFileHandler(
        filename=str(error_log_file),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # Очищаем старые логи при запуске
    cleanup_old_logs(log_dir, days=30)
    
    return root_logger


def cleanup_old_logs(log_dir='logs', days=30):
    """
    Удаляет логи старше указанного количества дней
    
    Args:
        log_dir: Директория с логами
        days: Количество дней для хранения логов
    """
    log_path = Path(log_dir)
    if not log_path.exists():
        return
    
    cutoff_time = time.time() - (days * 24 * 60 * 60)
    deleted_count = 0
    total_size_freed = 0
    
    try:
        # Проходим по всем файлам в директории логов
        for log_file in log_path.iterdir():
            if log_file.is_file():
                # Проверяем время модификации файла
                file_mtime = log_file.stat().st_mtime
                
                if file_mtime < cutoff_time:
                    file_size = log_file.stat().st_size
                    try:
                        log_file.unlink()
                        deleted_count += 1
                        total_size_freed += file_size
                    except Exception as e:
                        logging.warning(f"Не удалось удалить файл {log_file}: {e}")
        
        if deleted_count > 0:
            size_mb = total_size_freed / (1024 * 1024)
            logging.info(
                f"Очищено старых логов: {deleted_count} файлов, "
                f"освобождено {size_mb:.2f} MB"
            )
    except Exception as e:
        logging.error(f"Ошибка при очистке старых логов: {e}")


def get_log_files_info(log_dir='logs'):
    """
    Получить информацию о файлах логов
    
    Args:
        log_dir: Директория с логами
        
    Returns:
        dict: Информация о логах
    """
    log_path = Path(log_dir)
    if not log_path.exists():
        return {
            'total_files': 0,
            'total_size': 0,
            'files': []
        }
    
    files_info = []
    total_size = 0
    
    for log_file in sorted(log_path.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if log_file.is_file():
            file_size = log_file.stat().st_size
            file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            file_age = datetime.now() - file_mtime
            
            files_info.append({
                'name': log_file.name,
                'size': file_size,
                'size_mb': file_size / (1024 * 1024),
                'modified': file_mtime.strftime('%Y-%m-%d %H:%M:%S'),
                'age_days': file_age.days
            })
            total_size += file_size
    
    return {
        'total_files': len(files_info),
        'total_size': total_size,
        'total_size_mb': total_size / (1024 * 1024),
        'files': files_info
    }

