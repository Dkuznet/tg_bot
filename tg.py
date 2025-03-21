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


client = TelegramClient(
    session="anabot",
    api_id=API_ID,
    api_hash=API_HASH,
    system_version="21.5.2-zxc-cust",
    device_model="desk-win-custom",
    lang_code="ru",
    system_lang_code="ru-RU",
)


# Функция для авторизации
async def client_start():
    try:
        await client.start(phone=PHONE)  # type: ignore
        logger.info("Клиент успешно запущен!")
    except SessionPasswordNeededError:
        password = input("Введите пароль двухфакторной аутентификации: ")
        await client.start(phone=PHONE, password=password)  # type: ignore
        logger.info("Клиент успешно запущен с двухфакторной аутентификацией!")
    except Exception as e:
        logger.error(f"Ошибка при запуске клиента: {e}")
        raise


async def get_channel_messages(channel_username, limit=5):
    """Получение последних сообщений из канала"""
    # await client_start()
    if not client.is_connected():
        await client.connect()
    messages = []
    async for message in client.iter_messages(channel_username, limit=limit):
        if message.text:  # Проверяем, что сообщение содержит текст
            messages.append(
                {
                    "channel": channel_username,
                    "text": message.text,
                    "date": message.date.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
    return messages


# async def main():
# Getting information about yourself
# me = await client.get_me()

# "me" is a user object. You can pretty-print
# any Telegram object with the "stringify" method:
# print(me.stringify())

# When you print something, you see a representation of it.
# You can access all attributes of Telegram objects with
# the dot operator. For example, to get the username:
# username = me.username  # type: ignore
# print(username)
# print(me.phone)  # type: ignore

# You can print all the dialogs/conversations that you are part of:
# async for dialog in client.iter_dialogs():
#     print(dialog.name, "has ID", dialog.id)

# You can send messages to yourself...
# await client.send_message("me", "Hello, myself!")
# ...to some chat ID
# await client.send_message(-100123456, 'Hello, group!')
# ...to your contacts
# await client.send_message('+34600123123', 'Hello, friend!')
# ...or even to any username
# await client.send_message('username', 'Testing Telethon!')

# You can, of course, use markdown in your messages:
# message = await client.send_message(
#     "me",
#     "This message has **bold**, `code`, __italics__ and "
#     "a [nice website](https://example.com)!",
#     link_preview=False,
# )

# Sending a message returns the sent message object, which you can use
# print(message.raw_text)  # type: ignore

# You can reply to messages directly if you have a message object
# await message.reply('Cool!')

# Or send files, songs, documents, albums...
# await client.send_file('me', '/home/me/Pictures/holidays.jpg')

# You can print the message history of any chat:
# async for message in client.iter_messages('me'):
#     print(message.id, message.text)

# You can download media from messages, too!
# The method will return the path where the file was saved.
# if message.photo:
#     path = await message.download_media()
#     print('File saved to', path)  # printed after download is done

CHANNELS = ["@bitkogan", "@dimsmirnov175"]


async def start(update, context) -> None:
    """Обработчик команды /start"""
    await update.message.reply_text(
        text="Привет! Я бот, который читает новости из публичных каналов. Используй /news, чтобы получить последние новости."
    )


async def news(update, context) -> None:
    """Обработчик команды /news для получения новостей"""
    await update.message.reply_text("Собираю новости, подождите...")

    all_messages = []
    for channel in CHANNELS:
        messages = await get_channel_messages(channel)
        all_messages.extend(messages)

    if not all_messages:
        await update.message.reply_text("Новостей пока нет.")
        return

    # Сортировка сообщений по дате (от новых к старым)
    all_messages.sort(key=lambda x: x["date"], reverse=True)

    # Формирование текста для отправки пользователю
    response = "Последние новости:\n\n"
    response = f"собрал {len(all_messages)} новостей"
    await update.message.reply_text(response)

    for msg in all_messages[:2]:  # Ограничиваем до 10 новостей
        msg_text = f"{msg['channel']} ({msg['date']}):\n{msg['text']}\n\n"
        # print(msg_text)
        await update.message.reply_text(msg_text)


# Асинхронная функция для команды /stop
async def stop(update, context) -> None:
    await update.message.reply_text("Останавливаю бота...")
    await context.application.updater.stop()
    context.application.stop_running()  # Останавливаем Application
    logger.info("Бот остановлен.")


async def main():
    """Запуск бота"""

    # Попытка установить соединение, используя сохраненную сессию
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("User is not authorized. Starting authorization process...")
            await client_start()  # Start authentication flow.
        else:
            print("User is already authorized.")

        me = await client.get_me()
        print(f"Connected as {me.first_name} {me.last_name}")  # type: ignore

    except Exception as e:
        print(f"An error occurred: {e}")
    # finally:
    #     await client.disconnect()  # type: ignore

    # Создаём приложение для бота
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("news", news))

    # Инициализируем приложение
    await application.initialize()
    logger.info("Приложение инициализировано.")

    # Запускаем бота
    await application.start()
    logger.info("Бот запущен.")

    try:
        await application.updater.start_polling()  # type: ignore
        logger.info("Polling запущен.")

        await asyncio.Future()  # Keep the bot running indefinitely
    except asyncio.CancelledError:
        print("CancelledError caught. Shutting down gracefully...")
    finally:
        if client.is_connected():
            print("run await client.disconnect()")
            await client.disconnect()  # type: ignore
        print("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Программа завершена пользователем.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
