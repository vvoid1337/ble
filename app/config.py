import os

# Базовый URL для медиа (фото, видео). В БД хранятся ОТНОСИТЕЛЬНЫЕ пути
# (например "znamensky/cover.jpg"), а полная ссылка собирается на лету.
# Переезд на собственный CDN = смена одной этой переменной окружения.
MEDIA_BASE_URL = os.getenv(
    "MEDIA_BASE_URL",
    "https://raw.githubusercontent.com/vvoid1337/ble/master/media",
).rstrip("/")


def media_url(path: str | None) -> str | None:
    """Собрать абсолютный URL медиа из относительного пути.

    Если в БД уже лежит абсолютная ссылка (http/https) — возвращаем как есть,
    что позволяет при необходимости переопределять источник по конкретной записи.
    """
    if not path:
        return None
    if path.startswith(("http://", "https://")):
        return path
    return f"{MEDIA_BASE_URL}/{path.lstrip('/')}"
