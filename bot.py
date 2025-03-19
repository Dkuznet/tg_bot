import telebot

from dotenv import load_dotenv
import os


# Создаем экземпляр бота, указав токен, который вы получили от @BotFather в Telegram
load_dotenv()
TOKEN = str(os.environ.get("TELEGRAM_TOKEN"))

bot = telebot.TeleBot(TOKEN)


# Обработчик команды /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Привет! Я твой бот. Напиши что-нибудь, и я повторю. Используй /help для справки.",
    )


# Обработчик команды /help
@bot.message_handler(commands=["help"])
def send_help(message):
    bot.reply_to(
        message,
        "Я простой эхо-бот. Вот что я умею:\n/start - начать общение\n/help - показать эту справку\nПросто напиши текст, и я его повторю!",
    )


# Обработчик текстовых сообщений (эхо)
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)
