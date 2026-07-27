# Glass Player 🎵

Стильный музыкальный плеер в glassmorphism дизайне с интеграцией Яндекс Музыки.

## Быстрый старт (демо-режим)

Просто откройте `index.html` в браузере — работает с демо-треками.

## Подключение Яндекс Музыки

### Шаг 1: Установка Python-библиотеки

```bash
pip install yandex-music
```

### Шаг 2: Получение OAuth токена

1. Откройте в браузере:
   ```
   https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d
   ```
2. Войдите в аккаунт Яндекс
3. После редиректа скопируйте `access_token` из URL (после `#access_token=`)

### Шаг 3: Загрузка избранных треков

```bash
python fetch_favorites.py ВАШ_ТОКЕН
```

Альтернативно — авторизация через Device Flow (без токена):
```bash
python fetch_favorites.py --device-auth
```

Скрипт создаст `tracks.json` с вашими избранными треками.

### Шаг 4: Запуск сервера

```bash
cd server
npm install
node server.js
```

Сервер запустится на http://localhost:3000

### Шаг 5: Откройте плеер

Перейдите на http://localhost:3000 или откройте `index.html`.

В плеере нажмите ⚙️ (настройки), вставьте OAuth токен и адрес сервера.

## Горячие клавиши

| Клавиша | Действие |
|---------|----------|
| `Space` | Play/Pause |
| `←` | Предыдущий трек |
| `→` | Следующий трек |
| `↑` | Громкость +5% |
| `↓` | Громкость -5% |

## Структура проекта

```
music-player/
├── index.html          # Плеер (открыть в браузере)
├── tracks.json         # Треки из Яндекс Музыки (генерируется)
├── fetch_favorites.py  # Скрипт загрузки избранного
├── server/
│   ├── package.json    # Зависимости Node.js
│   └── server.js       # Прокси-сервер для аудио
└── README.md
```
