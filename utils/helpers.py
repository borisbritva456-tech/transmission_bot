def get_torrent_progress(torrent):
    """Получаем прогресс загрузки торрента в процентах"""
    try:
        # Пробуем разные возможные атрибуты для прогресса
        if hasattr(torrent, 'percentDone'):
            return torrent.percentDone * 100
        elif hasattr(torrent, 'progress'):
            return torrent.progress
        elif hasattr(torrent, 'percent_done'):
            return torrent.percent_done * 100
        else:
            # Если нет стандартных атрибутов, вычисляем вручную
            if hasattr(torrent, 'totalSize') and hasattr(torrent, 'sizeWhenDone'):
                if torrent.totalSize > 0:
                    return (torrent.sizeWhenDone / torrent.totalSize) * 100
            return 0
    except:
        return 0


def auth(update, chat_id):
    """Проверка прав пользователя"""
    return update.effective_chat.id == chat_id

