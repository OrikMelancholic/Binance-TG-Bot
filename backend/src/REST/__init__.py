import tornado.gen
from tornado.web import RequestHandler
from datetime import datetime, timedelta

from BinanceManager import BinanceManager as BinM
from Utilities import Logger

_version = "0.1"
_trusted_token = '03e2042c9fd8f6cdb946ddb123576736defff6ed1859cdce9ef6b34b008a97b9'
_logger = Logger('REST')
_binm = BinM()


def str2dt(time):
    return datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")


def response(handler, message=None, code=200):
    handler.set_status(code)
    resp = {'code': code, 'version': _version}
    if message:
        resp['message'] = message
    handler.write(resp)


class TeapotHandler(RequestHandler):
    def get(self):
        response(self, {'response': 'Я чайничек.'}, 418)


class AuthHandler(RequestHandler):
    @tornado.gen.coroutine
    def prepare(self):
        try:
            token = self.get_argument('token')
        except tornado.web.MissingArgumentError:
            response(self, 'Необходима авторизация.', 400)
            self.finish()
            return

        if token != _trusted_token:
            response(self, 'Неактивный токен.', 401)
            self.finish()


class LandingHandler(RequestHandler):
    def get(self):
        response(self, {})
        _logger.log('Got landing request')


class HistoryGetHandler(RequestHandler):
    def get(self):
        flair_pair = self.get_argument("symbol", default=None)
        flair_from = self.get_argument("from", default=None)
        flair_to = self.get_argument("to", default=None)

        if flair_pair and (flair_from or flair_to):
            response(self, 'Пара символов и отдельно символы не могут быть использованы одновременно.', 400)
            return

        if bool(flair_from) ^ bool(flair_to):
            response(self, 'Пара символов должна быть передана полностью.', 400)
            return

        if not (flair_pair or flair_to):
            response(self, 'Необходим символ или пара символов для исполнения команды.', 400)
            return

        if flair_from:
            flair_pair = flair_from + flair_to

        candle_size = self.get_argument("candle_size", default='1d')
        interval = self.get_argument("interval", default='07')
        date_from = self.get_argument("date_from", default=str(datetime.now() - timedelta(days=int(interval))))
        date_to = self.get_argument("date_to", default=str(datetime.now()))

        if str2dt(date_from) > str2dt(date_to):
            response(self, 'Время начала отсчёта должно быть до времени конца отсчёта.', 400)
            return

        data_in = {
            'symbol': flair_pair,
            'interval': candle_size,
            'start': date_from,
            'end': date_to,
        }
        _logger.log('HistoryGetHandler:\n%s' % _logger.fancy_json(data_in))
        data_out = _binm.getHistory(**data_in)
        _logger.log('Returning:\n%s' % _logger.fancy_json(data_out))
        response(self, data_out)


class CurrenciesGetHandler(RequestHandler):
    def get(self):
        flair = self.get_argument('flair', default=None)
        binance = self.get_argument('binance', default='False')
        binance = True if binance.lower() == 'true' else False

        data_in = {
            'flair': flair,
            'fromBinance': binance,
        }
        _logger.log('CurrenciesGetHandler:\n%s' % _logger.fancy_json(data_in))
        data_out = _binm.getCurrency(**data_in)
        _logger.log('Returning:\n%s' % _logger.fancy_json(data_out))
        response(self, data_out)


class CurrenciesUpdateHandler(AuthHandler):
    def get(self):
        flair = self.get_argument('flair', default=None)
        if not flair:
            response(self, 'Необходимо указать валюту для обновления.', 400)
            return

        data_in = {
            'flair': flair,
        }
        _logger.log('CurrenciesUpdateHandler:\n%s' % _logger.fancy_json(data_in))
        data_out = _binm.updateCurrency(**data_in)
        _logger.log('Returning:\n%s' % _logger.fancy_json(data_out))
        response(self, data_out)


class CurrenciesSubscribeHandler(TeapotHandler):
    pass


class RatesGetHandler(RequestHandler):
    def get(self):
        flair_pair = self.get_argument("symbol", default=None)
        flair_from = self.get_argument("from", default=None)
        flair_to = self.get_argument("to", default=None)

        if flair_pair and (flair_from or flair_to):
            response(self, 'Пара символов и отдельно символы не могут быть использованы одновременно.', 400)
            return

        binance = self.get_argument('binance', default='False')
        binance = True if binance.lower() == 'true' else False

        data_in = {
            'symbol': flair_pair,
            'flairFrom': flair_from,
            'flairTo': flair_to,
            'fromBinance': binance,
        }
        _logger.log('RatesGetHandler:\n%s' % _logger.fancy_json(data_in))
        data_out = _binm.getRates(**data_in)
        _logger.log('Returning:\n%s' % _logger.fancy_json(data_out))
        response(self, data_out)


class RatesSubscribeHandler(TeapotHandler):
    pass


class UserAssociateHandler(TeapotHandler):
    pass


class UserSubscribesGetHandler(TeapotHandler):
    pass


class UserUnsubscribeHandler(TeapotHandler):
    pass
