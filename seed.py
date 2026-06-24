"""Заливка контента из content/*.json в БД.

Запуск:  python seed.py

База (landmarks.db) в .gitignore, поэтому это единственный воспроизводимый
источник данных. Скрипт идемпотентен: пересоздаёт схему и заливает заново —
заодно убирает дубли и подхватывает изменения модели.
"""
import glob
import json
import os
import secrets

from app.database import Base, SessionLocal, engine
from app.models import Landmark

CONTENT_DIR = os.path.join(os.path.dirname(__file__), "content")

# Где живут авто-сгенерированные секреты меток. Отдельный gitignore-файл, а не
# content/*.json: контент можно коммитить, а секреты - нет.
# uuid (UPPER) -> hex. Явный "beacon_secret" в content/*.json (если задан) имеет приоритет.
SECRETS_FILE = os.path.join(CONTENT_DIR, "beacon_secrets.json")
SECRET_BYTES = 32  # ключ HMAC-SHA256

FIELDS = (
    "name",
    "subtitle",
    "year",
    "summary",
    "cover_image",
    "sections",
    "facts",
    "gallery",
)


def load_content() -> list[dict]:
    items = []
    for path in sorted(glob.glob(os.path.join(CONTENT_DIR, "*.json"))):
        # Сам файл секретов в content/ - это не достопримечательность, пропускаем.
        if os.path.abspath(path) == os.path.abspath(SECRETS_FILE):
            continue
        with open(path, encoding="utf-8") as f:
            items.append(json.load(f))
    return items


def load_secrets() -> dict[str, str]:
    """Прочитать стабильное хранилище секретов (uuid UPPER > hex). Нет файла — пустой словарь."""
    if not os.path.exists(SECRETS_FILE):
        return {}
    with open(SECRETS_FILE, encoding="utf-8") as f:
        return {str(k).upper(): str(v) for k, v in json.load(f).items()}


def save_secrets(store: dict[str, str]) -> None:
    os.makedirs(CONTENT_DIR, exist_ok=True)
    with open(SECRETS_FILE, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2, sort_keys=True, ensure_ascii=False)


def resolve_secret(data: dict, uuid_up: str, store: dict[str, str]) -> str:
    """hex-секрет метки. Приоритет: явный в content > сохранённый ранее > новый случайный.
    Новый секрет пишется в [store], чтобы повторный seed его сохранил"""
    explicit = (data.get("beacon_secret") or "").strip()
    if explicit:
        return explicit
    existing = store.get(uuid_up)
    if existing:
        return existing
    store[uuid_up] = secrets.token_hex(SECRET_BYTES)
    return store[uuid_up]


def main() -> None:
    # Пересоздаём схему целиком: модель могла измениться, а create_all не делает
    # ALTER. drop_all безопасен - seed по смыслу и так перезаливает всё заново.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    secret_store = load_secrets()
    secrets_before = len(secret_store)
    db = SessionLocal()
    try:
        for data in load_content():
            uuid_up = data["uuid"].upper()
            db.add(
                Landmark(
                    uuid=uuid_up,
                    beacon_secret=resolve_secret(data, uuid_up, secret_store),
                    # только присутствующие ключи - для отсутствующих сработает default модели
                    **{key: data[key] for key in FIELDS if key in data},
                )
            )
        db.commit()
        # Сохраняем хранилище, только если появились новые секреты (иначе файл не трогаем).
        if len(secret_store) != secrets_before:
            save_secrets(secret_store)
        count = db.query(Landmark).count()
        print(f"Seeded {count} landmarks ({len(secret_store)} beacon secrets in {SECRETS_FILE}).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
