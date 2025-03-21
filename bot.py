from typing import Any, Dict
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import logging
from dotenv import load_dotenv
from queue import Queue
import os

# Создаем очередь для хранения сообщений
message_queue = Queue()

# from telegram.ext._jobqueue import Job

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
CHANNEL_FILENAME = str(os.environ.get("CHANNEL_FILENAME"))


# async def read_file_async(filename: str) -> list[str]:
#     lines: list[str] = []
#     try:
#         async with aiofiles.open(filename, mode='r', encoding='utf-8') as file:
#             async for line in file:  # Асинхронное чтение построчно
#                 print(line.strip())  # Удаляем лишние пробелы и символы новой строки
#                 lines.append(line.strip())
#     except FileNotFoundError:
#         print(f"Файл {filename} не найден.")
#     except Exception as e:
#         print(f"Произошла ошибка: {e}")
#     return lines


def read_file(filename: str) -> list[str]:
    # Проверка, существует ли файл и является ли он файлом
    if os.path.isfile(filename):
        print(f"{filename} —  файл существует.")
    else:
        print(f"{filename} не существует, либо это не файл.")
        return [""]

    lines: list[str] = []
    try:
        with open(filename, mode="r", encoding="utf-8") as file:
            for line in file:  # Асинхронное чтение построчно
                print(line.strip())  # Удаляем лишние пробелы и символы новой строки
                lines.append(line.strip())
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    return lines


def write_file(filename: str, lines: list[str]) -> None:
    try:
        with open(filename, mode="w", encoding="utf-8") as file:
            for line in lines:
                if len(line) > 0:
                    file.write(line + "\n")
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


def load_channels() -> list[str]:
    channels = read_file(filename=CHANNEL_FILENAME)
    return channels


def update_channels(id: str):
    channels = load_channels()
    if id not in channels and len(id) > 0:
        channels.append(str(id))
        write_file(filename=CHANNEL_FILENAME, lines=channels)
    return f"update_channels {len(channels)}"


# Функция для обработки пересланных сообщений
async def handle_forwarded_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    message = update.message

    # Проверяем, является ли сообщение пересланным
    if message.forward_origin:  # type: ignore
        # Проверяем, что сообщение переслано из канала
        if (
            message.forward_origin.chat  # type: ignore
            and message.forward_origin.chat.type == "channel"  # type: ignore
        ):  # type: ignore
            chat = message.forward_origin.chat  # type: ignore
            await message.reply_text(f"Канал: {chat.title}, ID: {chat.id}")  # type: ignore

            # проверка на доступ
            try:
                chat = await context.bot.get_chat(chat.id)
                update_channels(str(chat.id))
            except Exception:
                print("Доступ к каналу ограничен.")
                await message.reply_text("Доступ к каналу ограничен.")  # type: ignore
        else:
            await message.reply_text("Это не канал.")  # type: ignore
    else:
        await message.reply_text(  # type: ignore
            "Перешлите сообщение из канала, чтобы я мог получить информацию."
        )


# Асинхронная функция для отправки периодических сообщений
async def send_periodic_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    if job is None:
        logger.error("Job is None in send_periodic_message.")
        return

    chat_id = job.data["chat_id"]  # type: ignore
    messages = job.data["messages"]  # type: ignore # Список сообщений для отправки
    if not messages.empty():
        id, message = messages.get()  # Берем первое сообщение из списка
        await context.bot.send_message(chat_id=chat_id, text=message)
        # Удаляем отправленное сообщение из списка (опционально, если нужно отправлять по очереди)
        # job.data["messages"] = messages[1:]  # type: ignore
    else:
        await context.bot.send_message(chat_id=chat_id, text="Список сообщений пуст.")


# Асинхронная функция для команды /start
async def start(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        logger.error("Update.message is None in start command.")
        return

    await update.message.reply_text(
        "Бот запущен! Используйте /stop_bot для остановки бота."
    )

    if context.job_queue is None:
        logger.error("JobQueue is not initialized.")
        await update.message.reply_text("JobQueue не инициализирован.")
        return

    # Инициализируем данные для JobQueue
    message_queue.put((1, "1am"))
    message_queue.put((2, "2bm"))

    job_data: Dict[str, Any] = {"chat_id": CHAT_ID, "messages": message_queue}

    # Запускаем периодическую задачу
    context.job_queue.run_repeating(
        callback=send_periodic_message,
        interval=10,  # Интервал в секундах
        first=0,  # Первая отправка сразу
        data=job_data,  # Передаем данные через параметр data
        # name=str(chat_id)  # Уникальное имя задачи для каждого чата
    )


# Асинхронная функция для команды /stop
async def stop(update, context):
    await update.message.reply_text("Останавливаю бота...")
    context.application.stop_running()  # Останавливаем Application
    logger.info("Бот остановлен.")


# Асинхронная функция для команды /list
async def list_ch(update, context):
    channels = read_file(filename=CHANNEL_FILENAME)
    names = []
    for ch_id in channels:
        if len(ch_id) > 0:
            try:
                chat = await context.bot.get_chat(int(ch_id))
                names.append(chat.title)
            except Exception:
                await update.message.reply_text(f"Доступ к каналу ограничен {ch_id}")

    message = "\n".join([str(i + 1) + ". " + n for i, n in enumerate(names)])

    chat_id = update.message.chat_id
    await context.bot.send_message(chat_id=chat_id, text=message)


async def collect_msg(update, context):
    # Получаем последние сообщения (можно ограничить количество)
    messages = await context.bot.get_updates(
        chat_id="-1001199979298",
        allowed_updates=["channel_post"],  # Фильтруем только сообщения из канала
        # offset=last_message_id, # Смещение относительно последнего сообщения
        limit=2,  #  или ограничьте кол-во сообщений
    )
    chat_id = update.message.chat_id
    for message in messages:
        await context.bot.send_message(chat_id=chat_id, text=message)


def main() -> None:
    """Основная функция для настройки и запуска бота."""
    # Создаем приложение (Application) для работы с ботом
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем команды
    application.add_handler(CommandHandler(command="start", callback=start))
    application.add_handler(CommandHandler(command="stop", callback=stop))
    application.add_handler(CommandHandler(command="list", callback=list_ch))
    application.add_handler(CommandHandler(command="collect", callback=collect_msg))
    application.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, handle_forwarded_message)
    )

    # Запускаем бота
    application.run_polling(allowed_updates=["message"])
    logger.info("Бот запущен.")


if __name__ == "__main__":
    # print(f"CHAT_ID {CHAT_ID}")
    main()
