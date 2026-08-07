import os
import asyncio
import threading

# Фикс цикла событий для новых версий Python
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from flask import Flask
from hydrogram import Client, filters
from hydrogram.types import Message

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

API_ID = int(os.environ.get("API_ID", 32991887))
API_HASH = os.environ.get("API_HASH", "ae3eb361f706d305320bf31071f9f3be")
STRING_SESSION = os.environ.get("STRING_SESSION")

bot = Client(
    "my_account",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)

@bot.on_message(filters.private & (filters.photo | filters.video))
async def save_ttl_media(client: Client, message: Message):
    media = message.photo or message.video
    if media and getattr(media, "ttl_seconds", None):
        try:
            # Скачиваем файл во временное хранилище
            file_path = await client.download_media(message)
            caption = f"Сохранено от @{message.from_user.username or message.from_user.id}"

            # Отправляем в Избранное
            if message.photo:
                await client.send_photo("me", photo=file_path, caption=caption)
            elif message.video:
                await client.send_video("me", video=file_path, caption=caption)

            # Удаляем копию с сервера Render
            if file_path and os.path.exists(file_path):
                os.remove(file_path)

            print(f"[УСПЕХ] Перехвачено медиа от {message.from_user.id}")
        except Exception as e:
            print(f"[ОШИБКА] {e}")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.run()