import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.src.plot_params import PlotParams
from bot.config import config as configs
from bot.config import markets as markets_list

from bot.src.binance_connector import BinanceConnector
from datetime import datetime, timedelta

plot_parameters = PlotParams()
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
        show_currencies_list()
    elif "mrkt_2" in query.data:
        currency = query.data.replace('mrkt_2_', '')
        print(f"currency => {currency}")
        bot.edit_message_text(chat_id=chat_id, message_id=last_bot_message_id, text=f"Выбранная валюта: {currency}")
        plot_parameters.currency = currency
        show_intervals_list()
    elif "mrkt_3" in query.data:
        days_count = int(query.data.replace('mrkt_3_', ''))
        print(f"days_count => {days_count}")
        bot.edit_message_text(chat_id=chat_id, message_id=last_bot_message_id,
                              text=f"Интервал для графика: {days_count} дней")
        plot_parameters.date_interval = days_count
        show_candles_list()
    elif "mrkt_4" in query.data:
        candle_size = query.data.replace('mrkt_4_', '')
        print(f"candle_size => {candle_size}")
        bot.edit_message_text(chat_id=chat_id, message_id=last_bot_message_id, text=f"Ширина свечи: {candle_size}")
        plot_parameters.candle_size = candle_size
        show_results()


def show_results():
    global last_bot_message_id

    bc = BinanceConnector()
    symbols = plot_parameters.currency + plot_parameters.market
    kline = plot_parameters.candle_size
    from_date = datetime.now() - timedelta(days=plot_parameters.date_interval)
    data = bc.get_data(symbols, kline, str(from_date))
    data_prepared = data['median'].to_numpy()
    length = data['Open time'].tolist()
    bc.plot(length, data_prepared)

    bot_message = bot.send_photo(chat_id=chat_id,
                                 photo=open("../figures/test_fig.png", 'rb'),
                                 parse_mode="markdown",
                                 caption=f"График изменения цены по следующим параметрам:\n"
                                         f"{plot_parameters.currency}/{plot_parameters.market}"
                                 )
    last_bot_message_id = bot_message.message_id


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


def show_currencies_list():
    global last_bot_message_id
    plot_parameters.current_stage = 2
    message = "Выберите валюту либо введите её код.\nПрим.: BTC"
    selected_market_code = plot_parameters.market
    if selected_market_code == "BNB":
        markets = ["ADA", "CREAM", "FARM", "CAKE", "SAND"]
    elif selected_market_code == "BTC":
        markets = ["DUSK", "DASH", "ATM", "1INCH", "POLY"]
    elif selected_market_code == "ETH":
        markets = ["BNB", "ETC", "HOT", "MFT", "NANO"]
    elif selected_market_code == "AUD":
        markets = ["BNB", "BTC", "ETH", "XRP", "LUNA"]
    elif selected_market_code == "RUB":
        markets = ["BNB", "BTC", "DOGE", "ETH", "USDT"]
    currency_buttons = []

    for currency_name in markets:
        currency_buttons.append([InlineKeyboardButton(currency_name, callback_data=f"mrkt_2_{currency_name}")])

    bot_message = bot.send_message(chat_id=chat_id,
                                   text=message,
                                   reply_markup=InlineKeyboardMarkup(currency_buttons))
    last_bot_message_id = bot_message.message_id


def show_intervals_list():
    global last_bot_message_id
    plot_parameters.current_stage = 3
    message = "Выберите интервал для графика:"

    interval_buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "День", callback_data="mrkt_3_01"
                )
            ],
            [
                InlineKeyboardButton(
                    "3 дня", callback_data="mrkt_3_03"
                )
            ],
            [
                InlineKeyboardButton(
                    "Неделя", callback_data="mrkt_3_07"
                )
            ],
            [
                InlineKeyboardButton(
                    "Месяц", callback_data="mrkt_3_30"
                )
            ],
            [
                InlineKeyboardButton(
                    "Три месяца", callback_data="mrkt_3_90"
                )
            ]
        ]
    )

    bot_message = bot.send_message(chat_id=chat_id,
                                   text=message,
                                   reply_markup=interval_buttons)
    last_bot_message_id = bot_message.message_id


def show_candles_list():
    global last_bot_message_id
    plot_parameters.current_stage = 4
    message = "Выберите ширину свечи для графика:"

    candle_buttons_std = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "15 Минут", callback_data="mrkt_4_15m"
                )
            ],
            [
                InlineKeyboardButton(
                    "1 Час", callback_data="mrkt_4_1h"
                )
            ],
            [
                InlineKeyboardButton(
                    "4 Часа", callback_data="mrkt_4_4h"
                )
            ],
            [
                InlineKeyboardButton(
                    "12 Часов", callback_data="mrkt_4_12h"
                )
            ],
            [
                InlineKeyboardButton(
                    "1 День", callback_data="mrkt_4_1d"
                )
            ]
        ]
    )

    candle_buttons_sml = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "15 Минут", callback_data="mrkt_4_15m"
                )
            ],
            [
                InlineKeyboardButton(
                    "1 Час", callback_data="mrkt_4_1h"
                )
            ],
            [
                InlineKeyboardButton(
                    "4 Часа", callback_data="mrkt_4_4h"
                )
            ]
        ]
    )

    if plot_parameters.date_interval == 1:
        buttons = candle_buttons_sml
    else:
        buttons = candle_buttons_std

    bot_message = bot.send_message(chat_id=chat_id,
                                   text=message,
                                   reply_markup=buttons)
    last_bot_message_id = bot_message.message_id


@bot.message_handler(content_types=['text'])
def handle_text(message):
    global last_bot_message_id

    if plot_parameters.current_stage == 2:
        currency_code = message.text
        selected_market = plot_parameters.market

        if markets_list.check_coin_in_market(currency_code, selected_market) == 0:
            bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        else:
            plot_parameters.currency = currency_code
            bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            bot.edit_message_text(chat_id=chat_id, message_id=last_bot_message_id,
                                  text=f"Выбранная валюта: {currency_code}")
            show_intervals_list()
    else:
        print("Не валюта", message.text)
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)


bot.infinity_polling()
