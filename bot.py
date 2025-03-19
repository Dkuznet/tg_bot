import telegram
from telegram.ext import (
    Application,
    JobQueue,
    ContextTypes,
    CommandHandler,
    CallbackContext,
)
from typing import Optional
import logging


# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ваш токен от BotFather
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = str(os.environ.get("TELEGRAM_TOKEN"))

if not BOT_TOKEN:
    print(
        "Ошибка: Не найден токен Telegram бота. Установите переменную окружения TELEGRAM_TOKEN или создайте файл .env."
    )
    exit()

# ID чата, куда отправлять сообщения (можно получить через @userinfobot или логирование)
CHAT_ID = "YOUR CHAT ID"
CHAT_ID = str(os.environ.get("TELEGRAM_CHAT_ID"))


# Функция для команды /start
async def start(update, context):
    update.message.reply_text("Бот запущен! Используйте /stop для остановки.")


# Функция для команды /stop
async def stop_bot(update, context):
    update.message.reply_text("Останавливаю бота...")
    context.application.stop_running()  # Останавливаем Application
    logger.info("Бот остановлен.")


async def send_periodic_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Функция, которая отправляет сообщение в чат."""
    message = "Привет! Это сообщение отправляется каждые 20 секунд."
    await context.bot.send_message(chat_id=CHAT_ID, text=message)
    print("Сообщение отправлено!")


def main() -> None:
    """Основная функция для настройки и запуска бота."""
    # Создаем приложение (Application) для работы с ботом
    application = Application.builder().token(BOT_TOKEN).build()

    # Получаем JobQueue из приложения с правильной аннотацией типа
    job_queue: Optional[JobQueue] = application.job_queue

    # Проверяем, что job_queue не None
    if job_queue is None:
        raise RuntimeError(
            "JobQueue не инициализирован. Убедитесь, что он включен в настройках Application."
        )

    # Регистрируем команды
    application.add_handler(CommandHandler(command="start", callback=start))
    application.add_handler(CommandHandler(command="stop bot", callback=stop_bot))

    # Планируем задачу отправки сообщения каждые 20 секунд
    job_queue.run_repeating(send_periodic_message, interval=10, first=0)

    # Запускаем бота
    application.run_polling(allowed_updates=[])


if __name__ == "__main__":
    # print(f"CHAT_ID {CHAT_ID}")
    main()
