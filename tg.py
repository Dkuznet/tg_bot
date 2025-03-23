import logging
import asyncio
from telethon import TelegramClient, events
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telethon.errors import SessionPasswordNeededError
from datetime import timedelta
import os
from config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    PHONE,
    CHANNEL_ID,
    CHANNELS_FILENAME,
    SESSION,
    SYSTEM_VERSION,
    DEVICE_MODEL,
    LANG_CODE,
    SYSTEM_LANG_CODE,
)

channels = {
    "name": [],
    "min_id": {},
    "messages": [],
}

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
    session=SESSION,
    api_id=API_ID,
    api_hash=API_HASH,
    system_version=SYSTEM_VERSION,
    device_model=DEVICE_MODEL,
    lang_code=LANG_CODE,
    system_lang_code=SYSTEM_LANG_CODE,
)


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
                # print(line.strip())  # Удаляем лишние пробелы и символы новой строки
                lines.append(line.strip())
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    return lines


def load_channels() -> list[str]:
    lines = read_file(filename=CHANNELS_FILENAME)
    names = []
    for line in lines:
        if len(line) > 0 and line[0] == "@":
            names.append(line.split("->")[0].strip())

    return list(set(names))


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


async def start(update, context) -> None:
    """Обработчик команды /start"""
    await update.message.reply_text(
        text="Привет! Я бот, который читает новости из публичных каналов. Используй /news, чтобы получить последние новости."
    )


CHANNELS = ["@bitkogan", "@dimsmirnov175"]


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
        # await update.message.reply_text(msg_text)
        await context.bot.send_message(chat_id=CHANNEL_ID, text=msg_text)


# Асинхронная функция для команды /stop
async def stop(update, context) -> None:
    await update.message.reply_text("Останавливаю бота...")
    await context.application.updater.stop()
    context.application.stop_running()  # Останавливаем Application
    logger.info("Бот остановлен.")


# Асинхронная функция для команды /send
async def send(update, context) -> None:
    await update.message.reply_text("Шлю текст в канал...")
    await context.bot.send_message(
        chat_id=CHANNEL_ID, text="This command only works in channels."
    )
    logger.info("Шлю текст в канал")


async def channel_message_handler(update, context) -> None:
    print("channel_message_handler")
    # Проверяем, что сообщение пришло из канала
    if update.channel_post:
        # Получаем текст сообщения
        message_text = update.channel_post.text
        message_id = update.channel_post.message_id
        chat_id = update.channel_post.chat_id  # ID канала
        chat_title = update.channel_post.chat.title  # Название канала

        # Ваша логика обработки сообщения
        print(
            f"Сообщение из канала '{chat_title}' (ID: {chat_id}): {message_text} (Message ID: {message_id})"
        )

        # Пример:  Отправка ответа в тот же канал
        await context.bot.send_message(
            chat_id=chat_id, text=f"Получено сообщение: {message_text}"
        )

        # Пример: Редактирование сообщения (ВАЖНО: у бота должны быть права администратора)
        # context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Измененное сообщение!")

        # Пример: Удаление сообщения (ВАЖНО: у бота должны быть права администратора)
        # context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    else:
        # Обработка других типов обновлений (если нужно)
        print("Это не сообщение из канала.")


async def safe_client_connect() -> None:
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


async def debug(update, context) -> None:
    await asyncio.sleep(2)
    await update.message.reply_text("Шлю много текст в канал...")
    print("Получено обновление:", update)


async def get_channel_messages(channel_name, min_id=0, limit_global=10):
    """Получение последних сообщений из канала"""

    if not client.is_connected():
        await client.connect()
    messages = []

    limit: int = 1 if min_id == 0 else limit_global
    max_id = min_id
    async for message in client.iter_messages(channel_name, min_id=min_id, limit=limit):
        max_id: int = max(max_id, message.id)
        if message.text and min_id > 0:  # Проверяем, что сообщение содержит текст
            # print(message.date, dir(message.date))
            dt = message.date + timedelta(hours=3)
            messages.append(
                {
                    "channel": channel_name,
                    "text": message.text,
                    "date": dt.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

    return messages, max_id


async def collect_new_messages(channel_name=None):
    print("collect_new_messages min_id counts:", len(channels["min_id"]))
    group_channels = channels["name"]
    if channel_name and channel_name in channels["name"]:
        group_channels = [channel_name]
    for channel_name in group_channels:
        min_id: int = channels["min_id"].get(channel_name, 0)
        new_messages, max_id = await get_channel_messages(
            channel_name=channel_name, min_id=min_id
        )
        channels["min_id"][channel_name] = max_id
        channels["messages"].extend(new_messages)
        await asyncio.sleep(0.1)

    # sort messages by date
    sorted_messages = sorted(
        channels["messages"], key=lambda x: x["date"], reverse=True
    )
    channels["messages"] = sorted_messages


def process_msg(message) -> str:
    short_msg = message["text"][:300]
    text: str = f"{message['channel']} {message['date']}\n{short_msg}"
    return text


import time

# start_update_time = 0


async def send_message(context) -> None:
    # global start_update_time
    # collect new messages
    # update_collection = time.time() - start_update_time
    # if len(channels["messages"]) < 1 and update_collection > 2 * 60:
    #     start_update_time = time.time()
    #     await collect_new_messages()

    size = len(channels["messages"])
    logger.info(f"collect_new_messages: {size}")
    if size == 0:
        return

    # process message
    message = channels["messages"].pop()

    # send to channel
    await context.bot.send_message(chat_id=CHANNEL_ID, text=process_msg(message))


async def bot_create():
    # Создаём приложение для бота
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(handler=CommandHandler(command="start", callback=start))
    application.add_handler(handler=CommandHandler(command="stop", callback=stop))
    application.add_handler(handler=CommandHandler(command="news", callback=news))

    # Добавляем задачу в JobQueue
    job_queue = application.job_queue
    job_queue.run_repeating(callback=send_message, interval=20, first=0)  # type: ignore # интервал в секундах

    # Инициализируем приложение
    await application.initialize()
    logger.info("Приложение инициализировано.")

    # Запускаем бота
    await application.start()
    logger.info("Бот запущен.")

    return application


async def print_channel_ids() -> None:
    # You can print all the dialogs/conversations that you are part of:
    async for dialog in client.iter_dialogs():
        if dialog.id < 0:
            print(dialog.name, "has ID", dialog.id)


async def print_channel_names() -> None:
    # You can print all the dialogs/conversations that you are part of:
    async for dialog in client.iter_dialogs():
        if dialog.id > 0:
            continue
        username, title = "", ""
        if hasattr(dialog.entity, "username") and dialog.entity.username:
            username = dialog.entity.username

        # if hasattr(dialog.entity, "tittle") and dialog.entity.tittle:
        title = dialog.name

        print("@" + username, "->", title)


@client.on(events.NewMessage)  # type: ignore
async def my_event_handler(event):
    print(f"Новое сообщение в канале {event.chat.title}: {event.message.text}")
    # Фильтруем сообщения по ID канала
    if event.is_channel:
        print("event.chat_id", event.chat_id)
        print("event.chat.username", event.chat.username)
        if event.chat.username in channels["name"]:
            await collect_new_messages(event.chat.username)

        # in channels["min_id"] : #Используем ID
    # Или, если вы хотите использовать имя канала:
    # if event.is_channel and event.chat.username == channel_username:
    # print(f"Новое сообщение в канале {event.chat.title}: {event.message.text}")
    # Здесь можно добавить код для обработки нового сообщения
    # Например, сохранение в базу данных, отправка уведомления и т.д.


async def main():
    """Запуск клиента и бота"""

    await safe_client_connect()

    # await print_channel_names()
    channels["name"] = load_channels()
    print(len(channels["name"]))
    print(channels["name"])

    application = await bot_create()

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
