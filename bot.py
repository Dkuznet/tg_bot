from telegram.ext import Application, JobQueue, ContextTypes
from typing import Optional
import logging

from dotenv import load_dotenv
import os

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ваш токен от BotFather
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

    # Планируем задачу отправки сообщения каждые 20 секунд
    job_queue.run_repeating(send_periodic_message, interval=10, first=0)

    # Запускаем бота
    application.run_polling(allowed_updates=[])


if __name__ == "__main__":
    main()
