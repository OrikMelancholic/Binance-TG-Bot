import telebot


bot = telebot.TeleBot('2133047644:AAHutBsvIFOcIJv9rqDJWNxgKxIKDUHhlkg')


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    bot.send_message(chat_id=chat_id,
                     text="Добро пожаловать.\nЭтот бот поможет в работе с Binance!")


bot.infinity_polling()
