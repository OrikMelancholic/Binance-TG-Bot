import matplotlib

from binobot.config import config as conf
from binance import Client
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
matplotlib.use('agg')


class BinanceConnector:

    def __init__(self):
        self.client = Client(api_key=conf.api_key, api_secret=conf.api_secret, tld='com')

    def ping_server(self):
        # Ping server if it's all OK
        if self.client.ping() == {}:
            return 'OK'
        else:
            return 'ERROR'

    def sever_time(self):
        # Test connectivity to the Rest API and get the current server time.
        # Returns:	Current server time
        return datetime.fromtimestamp(self.client.get_server_time()['serverTime'] / 1e3)

    def system_status(self):
        if self.client.get_system_status()['status'] == 0:
            return 'OK'
        else:
            return self.client.get_system_status()

    def list_all_cryptocurrency(self):
        # Latest price for all symbols
        # Returns:	List of market tickers
        return self.client.get_all_tickers()

    def symbol_info(self, symbol):
        # Return information about a symbol
        # Parameters:	symbol (str) – required e.g BNBBTC
        # Returns:	Dict if found, None if not
        return self.client.get_symbol_info(symbol)

    def get_data(self, symbol: str, interval: str, start_str: str, end_str=None) -> pd.DataFrame:
        # Parameters:
        #   symbol: Name of symbol pair e.g BNBBTC
        #   interval: Binance Kline interval
        #   start_str: Start date string in UTC format or timestamp in milliseconds
        #   end_str: optional - end date string in UTC format or timestamp in milliseconds
        #          (default will fetch everything up to now)
        data = []
        for kline in self.client.get_historical_klines_generator(symbol, interval, start_str, end_str):
            data.append(kline)
        df = pd.DataFrame(data)
        df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume first', 'Close time', 'Volume second',
                      'Number of trades', 'Buy volume first', 'Buy volume second', 'Ignore']
        #

        df['Open'] = df['Open'].astype(float)
        df['High'] = df['High'].astype(float)
        df['Close'] = df['Close'].astype(float)
        df['Low'] = df['Low'].astype(float)
        df['Volume first'] = df['Volume first'].astype(float)
        df['Volume second'] = df['Volume second'].astype(float)

        df['Open time'] = df['Open time'].astype(dtype='datetime64[ms]')
        df['Close time'] = df['Close time'].astype(dtype='datetime64[ms]')

        df.drop(['Ignore', 'Close time'], axis=1, inplace=True)
        pd.set_option('display.max_columns', 20)
        # print(df.info())
        df['median'] = (df['High'] + df['Low']) / 2

        return df

    def get_price_index(self, pair):
        # Parameters:	symbol (str) – name of the symbol pair
        # symbol='BTCUSDT'
        return self.client.get_margin_price_index(symbol=pair)

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

    def get_current_price(self, value_name): # in USD
        symbol = value_name + 'USDT'
        response = self.client.get_margin_price_index(symbol=symbol)
        return float(response['price'])
