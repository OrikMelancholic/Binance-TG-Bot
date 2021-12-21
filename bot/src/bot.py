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


def main_menu():
    global chat_id
    global last_bot_message_id

    menu = InlineKeyboardMarkup()
    menu.add(InlineKeyboardButton(text="Рынок", callback_data="mrkt"))
    menu.add(InlineKeyboardButton(text="Избранное", callback_data="fvrt"))

    bot_message = bot.send_message(chat_id=chat_id,
                                   text="Добро пожаловать.\nЭтот бот поможет в работе с Binance!",
                                   reply_markup=menu)
    last_bot_message_id = bot_message.message_id


@bot.callback_query_handler(lambda query: query.data.startswith("mrkt"))
def market_selection(query):
    global chat_id
    global last_bot_message_id

    print(f"query => {query.data}")
    if "mrkt" == query.data:
        bot.delete_message(chat_id=chat_id, message_id=last_bot_message_id)
        show_markets_list()
    elif "mrkt_1" in query.data:
        market = query.data.replace('mrkt_1_', '')
        print(f"market => {market}")
        bot.edit_message_text(chat_id=chat_id, message_id=last_bot_message_id, text=f"Выбранный рынок: {market}")


def show_markets_list():
    global last_bot_message_id
    message = "Выберите интересующий Вас рынок:"
    markets = ["BNB", "BTC", "ETH", "AUD", "RUB"]
    market_buttons = []

    for market_name in markets:
        market_buttons.append([InlineKeyboardButton(market_name, callback_data=f"mrkt_1_{market_name}")])

    bot_message = bot.send_message(chat_id=chat_id,
                                   text=message,
                                   reply_markup=InlineKeyboardMarkup(market_buttons))
    last_bot_message_id = bot_message.message_id


bot.infinity_polling()
