import telebot

from config import config as configs


token = configs.telebot_token
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    bot.send_message(chat_id=chat_id,
                     text="Добро пожаловать.\nЭтот бот поможет в работе с Binance!")


bot.infinity_polling()
