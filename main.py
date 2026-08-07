import os
import asyncio
import threading
from flask import Flask
from hydrogram import Client, filters
from hydrogram.types import Message

# 1. Запуск Flask-сервера для удержания Render в активном состоянии
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# 2. Настройки авторизации Telegram
API_ID = int(os.environ.get("API_ID", 32991887))
API_HASH = os.environ.get("API_HASH", "ae3eb361f706d305320bf31071f9f3be")
STRING_SESSION = os.environ.get("STRING_SESSION")

# Инициализация клиента
bot = Client(
    "my_account",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)

# 3. Хэндлер перехвата одноразовых фото и видео
@bot.on_message(filters.private & (filters.photo | filters.video))
async def save_ttl_media(client: Client, message: Message):
    # Проверяем, есть ли у медиафайла таймер самоуничтожения (ttl_seconds)
    media = message.photo or message.video
    if media and getattr(media, "ttl_seconds", None):
        try:
            # Скачиваем файл во временную папку
            file_path = await message.download()
            caption = f"Сохранено от @{message.from_user.username or message.from_user.id}"

            # Отправляем в "Избранное" (Saved Messages)
            if message.photo:
                await client.send_photo("me", photo=file_path, caption=caption)
            elif message.video:
                await client.send_video("me", video=file_path, caption=caption)

            # Удаляем локальный файл после отправки
            if os.path.exists(file_path):
                os.remove(file_path)

            print(f"[УСПЕХ] Одноразовое медиа от {message.from_user.id} сохранено в Избранное!")
        except Exception as e:
            print(f"[ОШИБКА] Не удалось сохранить медиа: {e}")

# 4. Точка входа
if __name__ == "__main__":
    # Запускаем Flask в фоновом потоке
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Запускаем Telegram-клиента
    bot.run()