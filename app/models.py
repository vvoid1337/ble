from sqlalchemy import JSON, Column, String, Text

from .database import Base


class Landmark(Base):
    __tablename__ = "landmarks"

    uuid = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    emoji = Column(String, nullable=False, default="")
    subtitle = Column(String, nullable=False, default="")   # короткий подзаголовок под названием
    year = Column(String, nullable=False, default="")
    summary = Column(Text, nullable=False, default="")      # лид-абзац (виден сразу)
    cover_image = Column(String, nullable=False, default="")  # относительный путь к обложке

    # Вики-подобный контент. Хранится как JSON — карточка целиком кэшируется
    # клиентом, поэтому реляционные таблицы и join'ы здесь избыточны.
    sections = Column(JSON, nullable=False, default=list)   # [{"title": str, "body": str}]
    facts = Column(JSON, nullable=False, default=list)      # ["факт", ...]
    gallery = Column(JSON, nullable=False, default=list)    # [{"type": "image|video", "src": str, "caption": str}]

    public_key = Column(Text, nullable=False, default="")   # резерв под infosec-трек (Challenge-Response)
