from sqlalchemy import Column, String, Text

from .database import Base


class Landmark(Base):
    __tablename__ = "landmarks"

    uuid = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    emoji = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    fact = Column(Text, nullable=False)
    year = Column(String, nullable=False)
    public_key = Column(Text, nullable=False, default="")
