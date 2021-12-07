import logging
from typing import Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
)

# Enable logging
from src.PlotParams import PlotParams
from config import config as configs
from src.binance_connector import BinanceConnector
from datetime import datetime, timedelta

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

plot_parameters = PlotParams()


# ########################### Selection #########################################
def favorites_selection(update, _: CallbackContext) -> None:
    query = update.callback_query
    query.answer()


def market_selection(update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    print(f"query => {query.data} ")

    update.effective_message.delete()
    if "mrkt" == query.data:
        plot_parameters.current_stage = 1
        show_markets_list(query)
    elif "mrkt_1" in query.data:
        if query.data == "mrkt_1_back":
            plot_parameters.current_stage = -1
            main_menu(query)
        else:
            market = query.data[-3:]
            plot_parameters.market = market
            plot_parameters.current_stage = 2
            show_currencies_list(query)
    elif "mrkt_2" in query.data:
        if query.data == "mrkt_2_back":
            plot_parameters.current_stage = 1
            show_markets_list(query)
        else:
            currency = query.data[-3:]
            plot_parameters.currency = currency
            plot_parameters.current_stage = 3
            show_intervals_list(query)
    elif "mrkt_3" in query.data:
        if query.data == "mrkt_3_back":
            plot_parameters.current_stage = 2
            show_currencies_list(query)
        else:
            days_count = int(query.data[-2:])
            print(days_count)
            plot_parameters.date_interval = days_count
            plot_parameters.current_stage = 4
            show_candles_list(query)
    elif "mrkt_4" in query.data:
        if query.data == "mrkt_4_back":
            plot_parameters.current_stage = 3
            show_intervals_list(query)
        else:
            candle_size = query.data.replace('mrkt_4_', '')
            plot_parameters.candle_size = candle_size
            show_results(query)


# ########################### Functions #########################################


def start(update, context):
    """Send a message when the command /start is issued."""
    buttons = [
        [InlineKeyboardButton("Рынок", callback_data="mrkt")],
        [InlineKeyboardButton("Избранное", callback_data="fvrt")]
    ]

    update.message.reply_text(
        text="Добро пожаловать.\nЭтот бот поможет в работе с Binance!",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def main_menu(query):
    buttons = [
        [InlineKeyboardButton("Рынок", callback_data="mrkt")],
        [InlineKeyboardButton("Избранное", callback_data="fvrt")]
    ]

    query.message.reply_text(
        text="Добро пожаловать.\nЭтот бот поможет в работе с Binance!",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def show_markets_list(query: Any):
    message = "Выберите интересующий Вас рынок:"
    markets = ["BTC", "BNB", "ETH", "TRX", "XRP"]
    market_buttons = []

    for market_name in markets:
        market_buttons.append([InlineKeyboardButton(market_name, callback_data=f"mrkt_1_{market_name}")])
    market_buttons.append([InlineKeyboardButton("Назад", callback_data=f"mrkt_1_back")])

    query.message.reply_text(
        reply_markup=InlineKeyboardMarkup(market_buttons),
        text=message)


def show_currencies_list(query: Any):
    message = "Выберите валюту либо введите её код (пока не вводите)"
    markets = ["BTC", "BNB", "ETH", "TRX", "XRP"]
    currency_buttons = []

    for currency_name in markets:
        currency_buttons.append([InlineKeyboardButton(currency_name, callback_data=f"mrkt_2_{currency_name}")])
    currency_buttons.append([InlineKeyboardButton("Назад", callback_data=f"mrkt_2_back")])

    query.message.reply_text(
        reply_markup=InlineKeyboardMarkup(currency_buttons),
        text=message)


def show_intervals_list(query: Any):
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

    query.message.reply_text(reply_markup=interval_buttons, text=message)


def show_candles_list(query: Any):
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

    query.message.reply_text(reply_markup=buttons, text=message)


def show_results(query: Any):
    symbols = plot_parameters.market + plot_parameters.currency
    kline = plot_parameters.candle_size
    to_date = datetime.now()
    from_date = to_date - timedelta(days=plot_parameters.date_interval)
    data = bc.get_data(symbols, kline, str(from_date))
    data_prepared = data['median'].to_numpy()
    length = data['Open time'].tolist()
    bc.plot(length, data_prepared)

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Глобальный минимум: 123", callback_data="mrkt_4_back"
                )
            ],
            [
                InlineKeyboardButton(
                    "Глобальный максимум: 123", callback_data="mrkt_4_back"
                )
            ],
            [
                InlineKeyboardButton(
                    "Цена: 123", callback_data="mrkt_4_back"
                )
            ],
            [
                InlineKeyboardButton(
                    "Соотношение: 123", callback_data="mrkt_4_back"
                )
            ],
            [
                InlineKeyboardButton(
                    "На главную", callback_data="mrkt_4_back"
                )
            ]
        ]
    )

    query.message.reply_photo(reply_markup=buttons,
                              photo=open("../figures/test_fig.png", 'rb'),
                              parse_mode="markdown",
                              caption=f"График изменения цены по следующим параметрам:\n"
                                      f"Рынок {plot_parameters.market}\n"
                                      f"Валюта {plot_parameters.currency}\n"
                                      f"Интервал {plot_parameters.date_interval}\n"
                                      f"Размер свечи {plot_parameters.candle_size}\n")


# ########################### Main #########################################
def main():
    # Create the Updater and pass it your bot's token.
    token = configs.telebot_token
    updater = Updater(token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    # ############################ Handlers #########################################
    updater.dispatcher.add_handler(
        CallbackQueryHandler(market_selection, pattern="mrkt")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(favorites_selection, pattern="fvrt")
    )

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    bc = BinanceConnector()
    main()
