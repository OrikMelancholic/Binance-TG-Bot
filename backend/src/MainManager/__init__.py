import sys

from backend.src.BinanceManager import BinanceManager

sys.path.append('..')

from backend.src.BinanceManager import BinanceManager as BinM
from backend.src.Utilities import Logger
import backend.src.REST
import backend.src.WebSocket

from tornado.web import Application
from tornado.ioloop import IOLoop


class MainManager:
    def __init__(self):
        self.logger = Logger('MainM')
        self.io_loop = IOLoop.current()
        self.binm = BinM(self.io_loop)
        params = {'binm': self.binm}
        self.urls = [
            ("/", backend.src.REST.LandingHandler),
            ("/history/get", backend.src.REST.HistoryGetHandler, params),
            ("/currencies/get", backend.src.REST.CurrenciesGetHandler, params),
            ("/currencies/update", backend.src.REST.CurrenciesUpdateHandler, params),
            ("/currencies/subscribe", backend.src.REST.CurrenciesSubscribeHandler, params),
            ("/currencies/unsubscribe", backend.src.REST.CurrenciesUnsubscribeHandler, params),
            ("/rates/get", backend.src.REST.RatesGetHandler, params),
            ("/user/associate", backend.src.REST.UserAssociateHandler, params),
            ("/user/subscriptions", backend.src.REST.UserSubscriptionsGetHandler, params),
            ("/push", backend.src.WebSocket.PushWebSockets, {'binm': self.binm, 'io_loop': self.io_loop}),
        ]
        self.application = Application(self.urls, debug=True)
        self.application.listen(8080)

    def start(self):
        self.io_loop.start()
