"""
Скрипт для получения избранных треков из Яндекс Музыки.

Перед запуском:
1. pip install yandex-music
2. Получить OAuth токен: https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d

Использование:
    python fetch_favorites.py YOUR_OAUTH_TOKEN
"""

import sys
import json
import os

def fetch_favorites(token: str):
    try:
        from yandex_music import Client
    except ImportError:
        print("Ошибка: установите библиотеку 'pip install yandex-music'")
        sys.exit(1)

    print("Подключение к Яндекс Музыке...")
    client = Client(token).init()

    print("Получение избранных треков...")
    likes = client.users_likes_tracks()
    tracks_short = likes.fetch_tracks()

    tracks = []
    for i, ts in enumerate(tracks_short):
        track = ts.track if hasattr(ts, 'track') else ts
        title = track.title
        artists = ", ".join(track.artists_name()) if track.artists else "Unknown"
        duration_ms = track.duration_ms if track.duration_ms else 0
        duration_sec = duration_ms // 1000
        minutes = duration_sec // 60
        seconds = duration_sec % 60
        duration_str = f"{minutes}:{seconds:02d}"

        # Получаем URL обложки
        cover_url = ""
        if track.cover_uri:
            cover_url = f"https://{track.cover_uri.replace('%%', '400x400')}"

        # Получаем URL аудио (для прокси)
        track_id = f"{track.id}:{track.albums[0].id}" if track.albums else str(track.id)

        album_title = track.albums[0].title if track.albums else ""

        tracks.append({
            "id": i,
            "title": title,
            "artist": artists,
            "album": album_title,
            "duration": duration_str,
            "duration_sec": duration_sec,
            "cover_url": cover_url,
            "track_id": track_id,
            "has_audio": True
        })
        print(f"  [{i+1}] {artists} - {title}")

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tracks.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tracks, f, ensure_ascii=False, indent=2)

    print(f"\nГотово! Сохранено {len(tracks)} треков в {output_path}")
    return tracks


def device_auth_flow():
    """Альтернативная авторизация через Device Flow (без токена)."""
    try:
        from yandex_music import Client
    except ImportError:
        print("Ошибка: установите библиотеку 'pip install yandex-music'")
        sys.exit(1)

    print("Запуск авторизации через Device Flow...")

    def on_code(code):
        print(f"\n{'='*50}")
        print(f"Откройте в браузере: {code.verification_url}")
        print(f"Введите код: {code.user_code}")
        print(f"{'='*50}\n")

    client = Client()
    token_obj = client.device_auth(on_code=on_code)

    print(f"\nАвторизация успешна!")
    print(f"Access Token: {token_obj.access_token}")
    print(f"\nСохраните токен для будущего использования.")
    print(f"Запустите скрипт снова: python fetch_favorites.py {token_obj.access_token}")

    return token_obj.access_token


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python fetch_favorites.py YOUR_OAUTH_TOKEN")
        print("  python fetch_favorites.py --device-auth")
        print()
        print("Получить токен: https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d")
        sys.exit(1)

    if sys.argv[1] == "--device-auth":
        token = device_auth_flow()
        if token:
            fetch_favorites(token)
    else:
        fetch_favorites(sys.argv[1])
