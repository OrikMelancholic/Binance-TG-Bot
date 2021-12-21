import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import config as configs

token = configs.telebot_token
bot = telebot.TeleBot(token)

last_bot_message_id = -1
chat_id = -1


@bot.message_handler(commands=['start'])
def start(message):
    global chat_id
    global last_bot_message_id

    chat_id = message.chat.id

    menu = InlineKeyboardMarkup()
    menu.add(InlineKeyboardButton(text="Рынок", callback_data="mrkt"))
    menu.add(InlineKeyboardButton(text="Избранное", callback_data="fvrt"))

    bot_message = bot.send_message(chat_id=message.chat.id,
                                   text="Добро пожаловать.\nЭтот бот поможет в работе с Binance!",
                                   reply_markup=menu)
    last_bot_message_id = bot_message.message_id


bot.infinity_polling()
