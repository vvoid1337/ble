"""Заливка контента из content/*.json в БД.

Запуск:  python seed.py

База (landmarks.db) в .gitignore, поэтому это единственный воспроизводимый
источник данных. Скрипт идемпотентен: пересоздаёт схему и заливает заново —
заодно убирает дубли и подхватывает изменения модели.
"""
import glob
import json
import os

from app.database import Base, SessionLocal, engine
from app.models import Landmark

CONTENT_DIR = os.path.join(os.path.dirname(__file__), "content")

FIELDS = (
    "name",
    "emoji",
    "subtitle",
    "year",
    "summary",
    "cover_image",
    "sections",
    "facts",
    "gallery",
    "public_key",
)


def load_content() -> list[dict]:
    items = []
    for path in sorted(glob.glob(os.path.join(CONTENT_DIR, "*.json"))):
        with open(path, encoding="utf-8") as f:
            items.append(json.load(f))
    return items


def main() -> None:
    # Пересоздаём схему целиком: модель могла измениться, а create_all не делает
    # ALTER. drop_all безопасен — seed по смыслу и так перезаливает всё заново.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for data in load_content():
            db.add(
                Landmark(
                    uuid=data["uuid"].upper(),
                    # только присутствующие ключи — для отсутствующих сработает default модели
                    **{key: data[key] for key in FIELDS if key in data},
                )
            )
        db.commit()
        count = db.query(Landmark).count()
        print(f"Seeded {count} landmarks.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
