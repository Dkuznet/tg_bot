import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
from dotenv import load_dotenv

load_dotenv()  # Загрузка переменных из .env

# Получаем токен из переменной окружения или файла .env
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    print(
        "Ошибка: Не найден токен Telegram бота. Установите переменную окружения TELEGRAM_TOKEN или создайте файл .env."
    )
    exit()


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Привет! Я твой Telegram-бот."
    )


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def caps(update, context):
    text_caps = " ".join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


def unknown(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Извините, я не понимаю эту команду."
    )


def error(update, context):
    """Log Errors caused by Updates."""
    print(f"Update {update} caused error {context.error}")


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("caps", caps, pass_args=True))

    # Обработчик эхо-сообщений
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))

    # Обработчик неизвестных команд
    dp.add_handler(MessageHandler(Filters.command, unknown))

    # Обработчик ошибок
    dp.add_error_handler(error)

    # Запуск бота
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

    # pip install python-telegram-bot
# pip install python-dotenv  # Для хранения токенов
