from pydantic import BaseModel

from .config import media_url


class Section(BaseModel):
    title: str
    body: str


class MediaItem(BaseModel):
    type: str            # "image" | "video"
    src: str             # абсолютный URL (собран из относительного пути)
    caption: str = ""


class LandmarkResponse(BaseModel):
    uuid: str
    name: str
    subtitle: str = ""
    year: str = ""
    summary: str = ""
    cover_image: str | None = None
    sections: list[Section] = []
    facts: list[str] = []
    gallery: list[MediaItem] = []
    # hex-секрет метки (TZ Вариант А): клиент кладёт его в Keystore и проверяет динамический
    # код. Симметричная схема => секрет уезжает на клиент (по HTTPS в проде).
    beacon_secret: str = ""

    @classmethod
    def from_landmark(cls, lm) -> "LandmarkResponse":
        """Построить ответ из ORM-объекта, развернув относительные пути в URL.

        Контент берётся из авторских JSON, поэтому собираем устойчиво к неполным
        элементам: секции без title/body нормализуются, а медиа без рабочего src
        отбрасываются — один кривой элемент не должен ронять весь ответ (500).
        """
        sections = [
            Section(title=s.get("title", ""), body=s.get("body", ""))
            for s in (lm.sections or [])
        ]

        gallery = []
        for item in lm.gallery or []:
            src = media_url(item.get("src"))
            if not src:
                continue  # пропускаем медиа без рабочей ссылки
            gallery.append(
                MediaItem(
                    type=item.get("type") or "image",
                    src=src,
                    caption=item.get("caption", ""),
                )
            )

        return cls(
            uuid=lm.uuid,
            name=lm.name,
            subtitle=lm.subtitle or "",
            year=lm.year or "",
            summary=lm.summary or "",
            cover_image=media_url(lm.cover_image),
            sections=sections,
            facts=[str(f) for f in (lm.facts or [])],
            gallery=gallery,
            beacon_secret=lm.beacon_secret or "",
        )
