import asyncio

import tornado.concurrent
from binance import Client
import sys
from datetime import timedelta
sys.path.append('..')

from Utilities import Logger
from DatabaseManager import DatabaseManager as DBM


class BinanceManager:
    def __init__(self, io_loop, dbm=None):
        # Who actually cares?
        self.api_key = 'jXepnmVYibuE2E6MsQ2TRHdBD4dkxEAA0HDucwoMXxNbNY3hPVmPB329VkYkY3cz'
        self.api_secret = 'na8CDIaNlIt7nlMcyndhVbb6cNbEtRRUVl9UfO0CCGOtlMYduuyimdwQySvYOpkH'
        self.client = Client(api_key=self.api_key, api_secret=self.api_secret, tld='com')
        self.logger = Logger('BinM')
        self.io_loop = io_loop
        self.push_stack = tornado.concurrent.Future()
        self.push_stack_delta = timedelta(seconds=30)
        self.logger.log('Binance update time set to: %s seconds' % self.push_stack_delta)
        if not dbm:
            self.dbm = DBM()

        self.io_loop.call_later(self.push_stack_delta.total_seconds(), self.binanceUpdate)

    def resetStack(self):
        self.logger.log('Future reset')
        self.push_stack = tornado.concurrent.Future()

    def binanceUpdate(self):
        data_db = self.dbm.getCurrency()
        data = {_[2]: _[1] for _ in data_db}
        new_events = []
        for flair in data.keys():
            data_binance = self.client.get_ticker(symbol=flair + 'USDT')
            current_price = float(data_binance['lastPrice'])
            data_db = self.dbm.getCurrencySubscription(flair=flair, active=True)
            if data_db:
                for _ in data_db:
                    if not _[3]:
                        continue
                    diffs = (data[flair] - _[3], current_price - _[3])
                    if diffs[0] * diffs[1] < 0:
                        new_events += [{
                            'flair': flair,
                            'price': current_price,
                            'user_id': _[-1],
                            'rising': diffs[1] > 0,
                        }]
                        self.CurrencySubscribe(_[-1], flair)
            self.dbm.updateCurrency(flair, current_price)
        if new_events:
            self.logger.log('New messages to websocket: %s' % new_events)
            self.push_stack.set_result(new_events)
            self.io_loop.call_later(2, self.resetStack)

        self.io_loop.call_later(self.push_stack_delta.total_seconds(), self.binanceUpdate)

    def getUsdValue(self, flair):
        symbol = flair + 'USDT'
        resp = self.client.get_margin_price_index(symbol=symbol)
        self.logger.log('Requested %s value in USD from Binance: %s' % (flair, resp['price']))
        return float(resp['price'])

    def getHistory(self, symbol, interval, start, end=None):
        if isinstance(symbol, tuple):
            symbol = ''.join(symbol)

        data = []
        keys = (
            'Open time', 'Open', 'High', 'Low', 'Close', 'Volume first', 'Close time', 'Volume second',
            'Number of trades', 'Buy volume first', 'Buy volume second', 'Ignore'
        )
        for kline in self.client.get_historical_klines_generator(symbol, interval, start, end):
            temp_dict = {}
            for _, key in enumerate(keys):
                temp_dict[key] = kline[_]
            data.append(temp_dict)
        self.logger.log('Requested %s history from Binance:\n%s' % (symbol, self.logger.fancy_json(data)))

        return data

    def getCurrency(self, flair=None, fromBinance=False):
        if fromBinance:
            if flair:
                raw_data = self.client.get_ticker(symbol=flair + 'USDT')
                data = [{'symbol': raw_data['symbol'], 'price': raw_data['lastPrice']}]
            else:
                data = self.client.get_all_tickers()
            data = [{'symbol': _['symbol'].replace('USDT', ''), 'price': _['price']} for _ in data if _['symbol'].endswith('USDT')]
            source = 'Binance'
        else:
            raw_data = self.dbm.getCurrency(flair)
            if flair:
                raw_data = [raw_data]
            data = [{'symbol': _[2], 'price': str(_[1])} for _ in raw_data]
            source = 'database'

        self.logger.log('Requested all currencies from %s:\n%s' % (source, self.logger.fancy_json(data)))
        return data

    def updateCurrency(self, flair):
        data_db = self.dbm.getCurrency(flair)
        data_binance = self.client.get_ticker(symbol=flair + 'USDT')['lastPrice']
        if data_db:
            data_db = self.dbm.updateCurrency(flair, data_binance)
        else:
            data_db = self.dbm.addCurrency(flair, data_binance)
        data = {'symbol': data_db[2], 'price': str(data_db[1])}

        self.logger.log('Requested %s update:\n%s' % (flair, self.logger.fancy_json(data)))
        return data

    def getRates(self, symbol=None, flairFrom=None, flairTo=None, fromBinance=False):
        nothing = not sum(map(bool, (symbol, flairFrom, flairTo)))
        if fromBinance:
            if symbol:
                raw_data = self.client.get_ticker(symbol=symbol)
                data = [{'symbol': raw_data['symbol'], 'price': raw_data['lastPrice']}]
            elif nothing:
                data = self.client.get_all_tickers()
            else:
                raw_data = self.client.get_all_tickers()
                data = []
                for _ in raw_data:
                    if flairFrom and not (_['symbol'].startswith(flairFrom)):
                        continue
                    if flairTo and not (_['symbol'].endswith(flairTo)):
                        continue
                    data += [_]
        else:
            raw_data = self.dbm.getCurrency()
            dict_data = {'USDT': 1}
            for _ in raw_data:
                dict_data[_[2]] = _[1]

            if symbol:
                valTo = 0
                valFrom = 0
                for _ in dict_data.keys():
                    if symbol.endswith(_):
                        valTo = dict_data[_]
                    if symbol.startswith(_):
                        valFrom = dict_data[_]
                if valTo and valFrom:
                    data = [{'symbol': symbol, 'price': str(valFrom/valTo)}]
                else:
                    data = []
            else:
                data = []
                for _flairFrom in dict_data.keys():
                    for _flairTo in dict_data.keys():
                        if _flairFrom == _flairTo:
                            continue
                        if flairFrom and (flairFrom != _flairFrom):
                            continue
                        if flairTo and (flairTo != _flairTo):
                            continue
                        data += [{'symbol': _flairFrom + _flairTo, 'price': str(dict_data[_flairFrom]/dict_data[_flairTo])}]

        flairs = {'symbol': symbol, 'flairFrom': flairFrom, 'flairTo': flairTo}
        self.logger.log('Requested rates via %s:\n%s' % (flairs, self.logger.fancy_json(data)))
        return data

    def CurrencySubscribe(self, tid, flair, target=None):
        self.updateCurrency(flair)
        data_db = self.dbm.getCurrencySubscription(tid, flair)
        if data_db:
            data_db = self.dbm.updateCurrencySubscription(tid, flair, target, 1)
        else:
            data_db = self.dbm.addCurrencySubscription(tid, flair, target)

        self.logger.log('Requested to subscribe %s to %s:\n%s' % (tid, flair, self.logger.fancy_json(data_db)))
        return {'success': bool(data_db)}

    def CurrencyUnsubscribe(self, tid, flair):
        data_db = self.dbm.getCurrencySubscription(tid, flair)
        if data_db:
            data_db = self.dbm.updateCurrencySubscription(tid, flair, active=0)
            self.logger.log('Requested to unsubscribe %s to %s:\n%s' % (tid, flair, self.logger.fancy_json(data_db)))
            return {'success': bool(data_db)}
        else:
            return {'success': False}

    def AssociateUser(self, tid):
        data_db = self.dbm.getUser(tid)
        if not data_db:
            data_db = self.dbm.addUser(tid)

        self.logger.log('Requested to associate Telegram user %s:\n%s' % (tid, self.logger.fancy_json(data_db)))
        return data_db

    def GetUserSubscriptions(self, tid):
        data = {}
        data_db = self.dbm.getCurrencySubscription(tid)
        if data_db:
            data_db = [{'flair': _[8], 'target': _[3]} for _ in data_db]
            data['currencies'] = data_db

        self.logger.log('Requested %s\'s subscriptions:\n%s' % (tid, self.logger.fancy_json(data)))
        return data
