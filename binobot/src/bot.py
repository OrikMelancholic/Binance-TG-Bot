import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from binobot.config import config as config, markets
from binobot.src.plot_params import PlotParams
from binobot.src.fav_params import FavParams
from binobot.src.binance_connector import BinanceConnector
from datetime import datetime, timedelta

plot_parameters = PlotParams()
fav_parameters = FavParams()
token = config.telebot_token
bot = telebot.TeleBot(token)

last_bot_message_id = -1
chat_id = -1

fav_list = []


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
    plot_parameters.current_stage = -1

    menu = InlineKeyboardMarkup()
    menu.add(InlineKeyboardButton(text="Рынок", callback_data="mrkt"))
    menu.add(InlineKeyboardButton(text="Избранное", callback_data="fvrt"))

    bot_message = bot.send_message(chat_id=chat_id,
                                   text="Добро пожаловать.\nЭтот бот поможет в работе с Binance!",
                                   reply_markup=menu)
    last_bot_message_id = bot_message.message_id


@bot.callback_query_handler(lambda query: query.data.startswith("fvrt"))
def market_selection(query):
    global chat_id
    global last_bot_message_id

    print(f"query => {query.data}")
    if "fvrt" == query.data:
        bot.delete_message(chat_id=chat_id, message_id=last_bot_message_id)
        show_favorites()
    elif "fvrt_back" in query.data:
        bot.delete_message(chat_id=chat_id, message_id=last_bot_message_id)
        main_menu()
    elif "fvrt_add" in query.data:
        bot.delete_message(chat_id=chat_id, message_id=last_bot_message_id)
        add_currency_to_fav_list()
    elif "fvrt_1" in query.data:
        if query.data == "fvrt_1_back":
            bot.delete_message(chat_id=chat_id, message_id=last_bot_message_id)
            show_favorites()
        else:
            market = query.data.replace('fvrt_1_', '')
            print(f"fav market => {market}")
            bot.edit_message_text(chat_id=chat_id, message_id=last_bot_message_id, text=f"Выбранный рынок: {market}")
    elif "fvrt_fav_" in query.data:
        if "fvrt_fav_delete" == query.data:
            print("remove shit")
            # Удалить подписку на валюту
        else:
            fav = query.data.replace('fvrt_fav_', '')
            bot.delete_message(chat_id=chat_id, message_id=last_bot_message_id)
            show_actions_menu(fav)


def show_favorites():
    global last_bot_message_id
    plot_parameters.current_stage = 1
    message = "У вас 3 подписки:"
    favorites = InlineKeyboardMarkup()

    for fav in fav_list:
        favorites.add(InlineKeyboardButton(text=fav, callback_data=f"fvrt_fav_{fav}"))

    favorites.add(InlineKeyboardButton("Добавить избранное", callback_data=f"fvrt_add"))
    favorites.add(InlineKeyboardButton("Назад", callback_data=f"fvrt_back"))

    bot_message = bot.send_message(chat_id=chat_id,
                                   text=message,
                                   reply_markup=favorites)
    last_bot_message_id = bot_message.message_id


def add_currency_to_fav_list():
    global last_bot_message_id
    fav_parameters.current_stage = 1
    message = "Введите код валюты, которую хотите добавить в избранное"
    back_button = InlineKeyboardMarkup()
    back_button.add(InlineKeyboardButton(text="Назад", callback_data=f"fvrt_1_back"))

    bot_message = bot.send_message(chat_id=chat_id, text=message, reply_markup=back_button)
    last_bot_message_id = bot_message.message_id


def show_actions_menu(selected_curr):
    global last_bot_message_id
    message = f"Текущая цена {selected_curr}: 0$\n" \
              f"Уведомления отсутствуют"
    buttons = InlineKeyboardMarkup()
    buttons.add(InlineKeyboardButton(text="Добавить уведомление об изменении цены",callback_data=f"fvrt_fav_notification"))
    buttons.add(InlineKeyboardButton(text="Удалить", callback_data=f"fvrt_fav_delete"))
    buttons.add(InlineKeyboardButton(text="Назад", callback_data=f"fvrt_1_back"))

    bot_message = bot.send_message(chat_id=chat_id, text=message, reply_markup=buttons)
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
        if query.data == "mrkt_1_back":
            bot.delete_message(chat_id=chat_id, message_id=last_bot_message_id)
            main_menu()
        else:
            market = query.data.replace('mrkt_1_', '')
            print(f"market => {market}")
            bot.edit_message_text(chat_id=chat_id, message_id=last_bot_message_id, text=f"Выбранный рынок: {market}")
            plot_parameters.market = market
            show_currencies_list()
    elif "mrkt_2" in query.data:
        if query.data == "mrkt_2_back":
            bot.delete_message(chat_id=chat_id, message_id=last_bot_message_id)
            show_markets_list()
        else:
            currency = query.data.replace('mrkt_2_', '')
            print(f"currency => {currency}")
            bot.edit_message_text(chat_id=chat_id, message_id=last_bot_message_id, text=f"Выбранная валюта: {currency}")
            plot_parameters.currency = currency
            show_intervals_list()
    elif "mrkt_3" in query.data:
        if query.data == "mrkt_3_back":
            bot.delete_message(chat_id=chat_id, message_id=last_bot_message_id)
            show_currencies_list()
        else:
            days_count = int(query.data.replace('mrkt_3_', ''))
            print(f"days_count => {days_count}")
            bot.edit_message_text(chat_id=chat_id, message_id=last_bot_message_id,
                                  text=f"Интервал для графика: {days_count} дней")
            plot_parameters.date_interval = days_count
            show_candles_list()
    elif "mrkt_4" in query.data:
        if query.data == "mrkt_4_back":
            bot.delete_message(chat_id=chat_id, message_id=last_bot_message_id)
            show_intervals_list()
        else:
            candle_size = query.data.replace('mrkt_4_', '')
            print(f"candle_size => {candle_size}")
            bot.edit_message_text(chat_id=chat_id, message_id=last_bot_message_id, text=f"Ширина свечи: {candle_size}")
            plot_parameters.candle_size = candle_size

            show_results()
    elif "mrkt_reset" in query.data:
        plot_parameters.reset()
        main_menu()


def show_markets_list():
    global last_bot_message_id
    plot_parameters.current_stage = 1
    message = "Выберите интересующий Вас рынок:"
    markets = ["BNB", "BTC", "ETH", "AUD", "RUB"]
    market_buttons = []

    for market_name in markets:
        market_buttons.append([InlineKeyboardButton(market_name, callback_data=f"mrkt_1_{market_name}")])
    market_buttons.append([InlineKeyboardButton("Назад", callback_data=f"mrkt_1_back")])

    bot_message = bot.send_message(chat_id=chat_id,
                                   text=message,
                                   reply_markup=InlineKeyboardMarkup(market_buttons))
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
            ],
            [
                InlineKeyboardButton(
                    "Назад", callback_data="mrkt_3_back"
                )
            ]
        ]
    )

    bot_message = bot.send_message(chat_id=chat_id,
                                   text=message,
                                   reply_markup=interval_buttons)
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
    currency_buttons.append([InlineKeyboardButton("Назад", callback_data=f"mrkt_2_back")])

    bot_message = bot.send_message(chat_id=chat_id,
                                   text=message,
                                   reply_markup=InlineKeyboardMarkup(currency_buttons))
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
            ],
            [
                InlineKeyboardButton(
                    "Назад", callback_data="mrkt_4_back"
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
            ],
            [
                InlineKeyboardButton(
                    "Назад", callback_data="mrkt_4_back"
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

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"Глобальный минимум: {bc.get_min(data_prepared)}", callback_data="mrkt_pass"
                )
            ],
            [
                InlineKeyboardButton(
                    f"Глобальный максимум: {bc.get_max(data_prepared)}", callback_data="mrkt_pass"
                )
            ],
            [
                InlineKeyboardButton(
                    f"Соотношение: {bc.get_current_pair_ratio(data_prepared)}", callback_data="mrkt_pass"
                )
            ],
            [
                InlineKeyboardButton(
                    f"Цена: {bc.get_current_price(plot_parameters.currency)} $", callback_data="mrkt_pass"
                )
            ],
            [
                InlineKeyboardButton(
                    "Главное меню", callback_data="mrkt_reset"
                )
            ]
        ]
    )

    bot_message = bot.send_photo(chat_id=chat_id,
                                 reply_markup=buttons,
                                 photo=open("../figures/test_fig.png", 'rb'),
                                 parse_mode="markdown",
                                 caption=f"График изменения цены по следующим параметрам:\n"
                                         f"{plot_parameters.currency}/{plot_parameters.market}"
                                 )
    last_bot_message_id = bot_message.message_id


@bot.message_handler(content_types=['text'])
def handle_text(message):
    global last_bot_message_id

    if plot_parameters.current_stage == 2:
        currency_code = message.text
        selected_market = plot_parameters.market

        if markets.check_coin_in_market(currency_code, selected_market) == 0:
            bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            bot_message = bot.send_message(
                chat_id=chat_id,
                text=f"Такой валюты ({currency_code}) на выбранном рынке не существует.\nПопробуйте заново.")
            last_bot_message_id = bot_message.message_id
        else:
            plot_parameters.currency = currency_code
            bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            bot.edit_message_text(chat_id=chat_id, message_id=last_bot_message_id,
                                  text=f"Выбранная валюта: {currency_code}")
            show_intervals_list()
    elif fav_parameters.current_stage == 1:
        currency_code = message.text.upper()

        if markets.check_usdt(currency_code) == 1:
            fav_parameters.currency = currency_code
            fav_list.append(currency_code)

            bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=last_bot_message_id,
                                  text=f"Валюта {currency_code} добавлена в избранные")
            show_favorites()
        else:
            bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            bot_message = bot.send_message(
                chat_id=chat_id,
                text=f"Такой валюты ({currency_code}) на рынке USDT не существует.\nПопробуйте заново.")
            last_bot_message_id = bot_message.message_id
    else:
        print("Не ало", message.text)
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)


bot.infinity_polling()
