# Курск 1000 — Backend

Бэкенд-контент для мобильного гида «BLE-Гид: Курск 1000». Отдаёт вики-подобные
карточки достопримечательностей (текст по секциям, факты, галерея фото/видео),
привязанные к UUID BLE-меток. Клиент кэширует данные локально (Room), TTS
(«озвучить») выполняется на стороне клиента.

## Запуск

```powershell
python -m pip install -r requirements.txt
python seed.py                       # залить контент из content/*.json в БД
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Структура контента

- `content/*.json` — исходный контент, по файлу на достопримечательность. Это
  основной редактируемый источник; БД (`landmarks.db`) в `.gitignore` и
  пересоздаётся скриптом `seed.py`.
- `media/` — фото и видео. Раздаются через `raw.githubusercontent.com`, в БД
  хранятся **относительные** пути. ⚠️ Сами ассеты пока не добавлены —
  ожидаемую структуру и имена файлов см. в `media/README.md`; до их загрузки
  ссылки на изображения будут отдавать `404`.

### Медиа и CDN

Полный URL медиа собирается из `MEDIA_BASE_URL` (см. `app/config.py`,
по умолчанию `raw.githubusercontent.com/vvoid1337/ble/master/media`).
Переезд на собственный CDN — сменить одну переменную окружения, пути в БД и
контенте не трогаются:

```powershell
$env:MEDIA_BASE_URL = "https://cdn.example.com/media"   # PowerShell
```

```bash
export MEDIA_BASE_URL="https://cdn.example.com/media"    # bash/zsh
```

## API

### `GET /landmarks`

Все достопримечательности целиком — для первичного кэширования на клиенте.

```json
[
  {
    "uuid": "A1B2C3D4-E5F6-7890-ABCD-EF1234567890",
    "name": "Знаменский собор",
    "emoji": "⛪️",
    "subtitle": "Православный кафедральный собор · 1816–1826",
    "year": "1816",
    "summary": "Лид-абзац…",
    "cover_image": "https://raw.githubusercontent.com/vvoid1337/ble/master/media/znamensky-sobor/cover.jpg",
    "sections": [
      { "title": "История", "body": "…" }
    ],
    "facts": ["…"],
    "gallery": [
      { "type": "image", "src": "https://…/znamensky-sobor/01.jpg", "caption": "Главный фасад" }
    ],
    "public_key": ""
  }
]
```

### `GET /landmark/{uuid}`

Одна достопримечательность по UUID метки (регистр не важен). `404`, если не найдена.

```text
http://localhost:8000/landmark/A1B2C3D4-E5F6-7890-ABCD-EF1234567890
```

> `/landmark/{uuid}` оставлен для совместимости; при полном кэшировании на
> клиенте достаточно одного `GET /landmarks`.

## Поле `public_key`

Зарезервировано под infosec-трек (Challenge-Response): публичный ключ
достопримечательности для проверки подписи метки. Пока пустое.

## Добавить достопримечательность

1. Создать `content/<slug>.json` (UUID, name, emoji, subtitle, year, summary,
   cover_image, sections, facts, gallery, public_key).
2. Положить медиа в `media/<slug>/…` с теми же именами, что в JSON.
3. `python seed.py`.
