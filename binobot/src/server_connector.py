import matplotlib
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt

import sys
sys.path.append('../..')

from binobot.src.websocket import WebSocket

matplotlib.use('agg')

date_format = '%Y-%m-%d %H:%M:%S.%f'
token = '03e2042c9fd8f6cdb946ddb123576736defff6ed1859cdce9ef6b34b008a97b9'


class ServerConnector:
    def __init__(self, bot):
        self.base_url = 'http://api.salieri.me/'
        self.bot = bot
        self.ws = WebSocket('ws://api.salieri.me/push?token=%s' % token, self.bot)
        self.ws.start()
        self.ws.connect()

    def get_smth(self, method, **params):
        url = '%s/%s' % (self.base_url, method)
        r = requests.get(url, params=params)
        payload = json.loads(r.content)
        return payload

    def get_history_data(self, symbol, candle_size=None, start=None):
        data = self.get_smth('/history/get', symbol=symbol, candle_size=candle_size, date_from=start)
        df = pd.DataFrame(data['message'])
        df['High'] = df['High'].astype(float)
        df['Low'] = df['Low'].astype(float)
        df['median'] = (df['High'] + df['Low']) / 2
        df['Open time'] = df['Open time'].astype(dtype='datetime64[ms]')
        df.drop(['Ignore', 'Close time'], axis=1, inplace=True)
        df.drop(['Open', 'Close', 'Volume first', 'Volume second', 'Number of trades', 'Buy volume first',
                 'Buy volume second', 'Low', 'High'], axis=1, inplace=True)
        return df

    def get_currencies(self, flair, binance=False):
        data = self.get_smth('currencies/get', flair=flair, binance=binance)
        return data['message'][0]['price']

    def get_rates(self, symbol, binance=False):
        data = self.get_smth('rates/get', symbol=symbol, binance=binance)
        return data['message'][0]['price']

    def plot(self, time, data):
        # Parameters:
        #   time (list of timestamps) - X axis
        #   data (list of values) - Y data
        plt.subplot(1, 1, 1)
        plt.plot(time, data)
        plt.gcf().autofmt_xdate()
        plt.savefig('../figures/test_fig.png')
        plt.close()

    def get_min(self, data):
        return min(data)

    def get_max(self, data):
        return max(data)

    def get_current_pair_ratio(self, data):
        return data[-1]

    def get_current_price(self, value_name):  # in USD
        return self.get_currencies(value_name, binance=True)

    def associate_user(self, tg_user_id):
        data = self.get_smth("/user/associate", tid=tg_user_id, token=token)
        return data

    def get_subscriptions(self, user_id):
        data = self.get_smth("/user/subscriptions", tid=user_id, token=token)
        if 'message' in data:
            return data['message']
        else:
            return {}

    def active_subscription(self, user_id, currency):
        data = self.get_smth("/user/subscriptions", tid=user_id, token=token)
        if 'message' in data:
            for i in data['message']['currencies']:
                if i['flair'] == currency and i['target'] is not None:
                    return i['target']
            return {}
        else:
            return {}

    def add_subscription(self, user_id, currency, target=None):
        data = self.get_smth("/currencies/subscribe", tid=user_id, flair=currency, target=target, token=token)
        if 'code' in data and data['code'] == 200:
            return True
        else:
            return False

    def remove_subscription(self, user_id, currency):
        data = self.get_smth("/currencies/unsubscribe", tid=user_id, flair=currency, token=token)
        if 'code' in data and data['code'] == 200:
            return True
        else:
            return False
