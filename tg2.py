import asyncio
import nest_asyncio
import telegram
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telethon import TelegramClient, events

import logging
import asyncio
from telethon import TelegramClient
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telethon.errors import FloodWaitError, RPCError, SessionPasswordNeededError
from config import API_ID, API_HASH, BOT_TOKEN, PHONE


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("tg.log"),  # Логи будут сохраняться в файл
        logging.StreamHandler(),  # Логи будут выводиться в консоль
    ],
)
logger = logging.getLogger(__name__)

telethon_client = TelegramClient(
    session="anabot",
    api_id=API_ID,
    api_hash=API_HASH,
    system_version="21.5.2-zxc-cust",
    device_model="desk-win-custom",
    lang_code="ru",
    system_lang_code="ru-RU",
)


# --- telegram.ext (python-telegram-bot) ---
async def bot_main() -> None:
    # Create a new event loop for the bot
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Создаём приложение для бота
    application = Application.builder().token(BOT_TOKEN).build()

    async def start(update, context) -> None:
        """Обработчик команды /start"""
        await update.message.reply_text(
            text="Привет! Я бот, который читает новости из публичных каналов. Используй /news, чтобы получить последние новости."
        )

    # Асинхронная функция для команды /stop
    async def stop(update, context) -> None:
        await update.message.reply_text("Останавливаю бота...")
        context.application.stop_running()  # Останавливаем Application
        logger.info("Бот остановлен.")

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    # application.add_handler(CommandHandler("news", news))

    # Start the bot
    try:
        await application.run_polling()  # type: ignore
        logger.info("Бот запущен.")
    finally:
        await application.shutdown()  # Properly shutdown the application


# Функция для авторизации
async def client_start():
    try:
        await telethon_client.start(phone=PHONE)  # type: ignore
        logger.info("Клиент успешно запущен!")
    except SessionPasswordNeededError:
        password = input("Введите пароль двухфакторной аутентификации: ")
        await telethon_client.start(phone=PHONE, password=password)  # type: ignore
        logger.info("Клиент успешно запущен с двухфакторной аутентификацией!")
    except Exception as e:
        logger.error(f"Ошибка при запуске клиента: {e}")
        raise


# --- Telethon ---
async def telethon_main() -> None:
    try:
        await telethon_client.connect()
        if not await telethon_client.is_user_authorized():
            print("User is not authorized. Starting authorization process...")
            await client_start()  # Start authentication flow.
        else:
            print("User is already authorized.")

        me = await telethon_client.get_me()
        print(f"Connected as {me.first_name} {me.last_name}")  # type: ignore

    except Exception as e:
        print(f"An error occurred: {e}")

    await telethon_client.run_until_disconnected()  # type: ignore


# --- Main ---
# async def main():
#     # Create tasks
#     telethon_task = asyncio.create_task(telethon_main())
#     bot_task = asyncio.create_task(bot_main())

#     # Run tasks concurrently
#     await asyncio.gather(telethon_task, bot_task)


# if __name__ == "__main__":
#     asyncio.run(main())


import asyncio
import signal
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telethon import TelegramClient, events


# Обработчик команды для бота
async def start_command(update, context):
    await update.message.reply_text("Привет! Я работаю вместе с Telethon!")


# Обработчик сообщений для Telethon
async def handle_telethon_message(event):
    print(f"Получено сообщение через Telethon: {event.text}")


# Флаг для контроля работы цикла
running = True


# Асинхронная функция для команды /stop
async def stop_command(update, context) -> None:
    await update.message.reply_text("Останавливаю бота...")
    context.application.stop_running()  # Останавливаем Application
    logger.info("Бот остановлен.")


async def main():
    # Инициализация Telethon
    await telethon_client.connect()  # type: ignore

    # Инициализация бота
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("stop", stop_command))

    # Запуск бота (неблокирующий режим)
    await application.initialize()
    await application.start()
    await application.updater.start_polling()  # type: ignore

    # Поддержка работы скрипта
    try:
        print("Оба клиента запущены!")
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        # Корректное завершение работы
        await telethon_client.disconnect()  # type: ignore
        await application.stop()


if __name__ == "__main__":
    asyncio.run(main())
