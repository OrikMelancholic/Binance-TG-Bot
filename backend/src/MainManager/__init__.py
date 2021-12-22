import sys
sys.path.append('..')

from BinanceManager import BinanceManager as BinM
from Utilities import Logger
import REST
import WebSocket

from tornado.web import Application
from tornado.ioloop import IOLoop


class MainManager:
    def __init__(self):
        self.logger = Logger('MainM')
        self.io_loop = IOLoop.current()
        self.binm = BinM(self.io_loop)
        params = {'binm': self.binm}
        self.urls = [
            ("/", REST.LandingHandler),
            ("/history/get", REST.HistoryGetHandler, params),
            ("/currencies/get", REST.CurrenciesGetHandler, params),
            ("/currencies/update", REST.CurrenciesUpdateHandler, params),
            ("/currencies/subscribe", REST.CurrenciesSubscribeHandler, params),
            ("/currencies/unsubscribe", REST.CurrenciesUnsubscribeHandler, params),
            ("/rates/get", REST.RatesGetHandler, params),
            ("/user/associate", REST.UserAssociateHandler, params),
            ("/user/subscriptions", REST.UserSubscriptionsGetHandler, params),
            ("/push", WebSocket.PushWebSockets, {'binm': self.binm, 'io_loop': self.io_loop}),
        ]
        self.application = Application(self.urls, debug=True)
        self.application.listen(8080)

    def start(self):
        self.io_loop.start()
