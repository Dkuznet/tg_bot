import logging
import asyncio
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, RPCError, SessionPasswordNeededError
from config import API_ID, API_HASH, PHONE, PASSWORD

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),  # Логи будут сохраняться в файл
        logging.StreamHandler(),  # Логи будут выводиться в консоль
    ],
)
logger = logging.getLogger(__name__)

# Создание клиента
SESSION_NAME = "bot_session"
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


# Функция для авторизации
async def start_client():
    try:
        await client.start(phone=PHONE)  # type: ignore
        logger.info("Клиент успешно запущен!")
    except SessionPasswordNeededError:
        # password = input("Введите пароль двухфакторной аутентификации: ")
        await client.start(phone=PHONE, password=PASSWORD)  # type: ignore
        logger.info("Клиент успешно запущен с двухфакторной аутентификацией!")
    except Exception as e:
        logger.error(f"Ошибка при запуске клиента: {e}")
        raise


# Обработчик команды /start
@client.on(events.NewMessage(pattern=r"^/start$"))
async def start_handler(event):
    try:
        user = await event.get_sender()
        await event.reply(
            f"Привет, {user.first_name}! Я бот, готовый помочь.\n"
            "Доступные команды:\n"
            "/start - Начать работу\n"
            "/help - Получить помощь"
        )
        logger.info(f"Команда /start выполнена для пользователя {user.id}")
    except FloodWaitError as e:
        logger.error(f"Слишком много запросов. Ждем {e.seconds} секунд.")
        await asyncio.sleep(e.seconds)
        await event.reply("Пожалуйста, подождите немного и попробуйте снова.")
    except RPCError as e:
        logger.error(f"Ошибка Telegram API: {e}")
        await event.reply("Произошла ошибка. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        await event.reply("Произошла неизвестная ошибка. Обратитесь к администратору.")


# Обработчик команды /help
@client.on(events.NewMessage(pattern=r"^/help$"))
async def help_handler(event):
    try:
        await event.reply(
            "Список доступных команд:\n"
            "/start - Начать работу\n"
            "/help - Получить помощь\n"
            "Просто напишите мне что-нибудь, и я отвечу!"
        )
        logger.info(f"Команда /help выполнена для пользователя {event.sender_id}")
    except FloodWaitError as e:
        logger.error(f"Слишком много запросов. Ждем {e.seconds} секунд.")
        await asyncio.sleep(e.seconds)
        await event.reply("Пожалуйста, подождите немного и попробуйте снова.")
    except RPCError as e:
        logger.error(f"Ошибка Telegram API: {e}")
        await event.reply("Произошла ошибка. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        await event.reply("Произошла неизвестная ошибка. Обратитесь к администратору.")


# Обработчик всех текстовых сообщений (эхо)
@client.on(events.NewMessage)  # type: ignore
async def echo_handler(event):
    try:
        if event.is_private and not event.out:  # Только личные сообщения, не от бота
            message_text = event.text.lower()
            if message_text.startswith("/"):  # Игнорируем команды
                return
            await event.reply(
                f"Вы написали: {event.text}\nЯ эхо-бот, повторяю за вами!"
            )
            logger.info(f"Эхо-сообщение отправлено пользователю {event.sender_id}")
    except FloodWaitError as e:
        logger.error(f"Слишком много запросов. Ждем {e.seconds} секунд.")
        await asyncio.sleep(e.seconds)
    except RPCError as e:
        logger.error(f"Ошибка Telegram API: {e}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")


# Главная функция для запуска бота
async def main():
    await start_client()
    logger.info("Бот запущен и готов к работе!")
    await client.run_until_disconnected()  # type: ignore


if __name__ == "__main__":
    try:
        with client:
            client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем.")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
