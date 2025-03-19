import telegram
from telegram.ext import Application, CommandHandler
import asyncio
import schedule
import logging
import threading
import time

from dotenv import load_dotenv
import os

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ваш токен от BotFather
load_dotenv()
TOKEN = str(os.environ.get("TELEGRAM_TOKEN"))

if not TOKEN:
    print(
        "Ошибка: Не найден токен Telegram бота. Установите переменную окружения TELEGRAM_TOKEN или создайте файл .env."
    )
    exit()

# ID чата, куда отправлять сообщения (можно получить через @userinfobot или логирование)
CHAT_ID = "YOUR_CHAT_ID"

# Инициализация бота
bot = telegram.Bot(token=TOKEN)


# Асинхронная функция для отправки сообщения
async def send_message():
    try:
        await bot.send_message(
            chat_id=CHAT_ID, text="Привет! Это сообщение отправляется раз в минуту."
        )
        logger.info("Сообщение успешно отправлено!")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")


# Функция для запуска асинхронного цикла событий (для отправки сообщений)
def run_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()


# Функция для запуска планировщика в отдельном потоке
def run_scheduler():
    schedule.every(interval=1).minutes.do(
        lambda: asyncio.run_coroutine_threadsafe(
            send_message(), asyncio.get_event_loop()
        )
    )
    while True:
        schedule.run_pending()
        time.sleep(1)


# Команда /start для проверки работы бота
async def start(update, context):
    await update.message.reply_text(
        "Бот запущен! Я буду отправлять сообщение каждую минуту."
    )
    # Если вы не знаете ваш CHAT_ID, раскомментируйте следующую строку, чтобы узнать его
    # await update.message.reply_text(f"Ваш CHAT_ID: {update.message.chat_id}")


# Основная функция
def main():
    # Создаем Application (новый способ работы с python-telegram-bot)
    application = Application.builder().token(TOKEN).build()

    # Регистрируем команду /start
    application.add_handler(CommandHandler("start", start))

    # Запускаем асинхронный цикл событий в отдельном потоке
    async_loop_thread = threading.Thread(target=run_async_loop, daemon=True)
    async_loop_thread.start()

    # Запускаем планировщик в отдельном потоке
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Запускаем бота (это блокирует основной поток)
    logger.info("Бот запущен!")
    application.run_polling(allowed_updates=None)


if __name__ == "__main__":
    main()
