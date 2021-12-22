import sys
sys.path.append('..')

from BinanceManager import BinanceManager as BinM
from Utilities import Logger
import REST

from tornado.web import Application
from tornado.ioloop import IOLoop


class MainManager:
    def __init__(self):
        self.logger = Logger('MainM')
        self.binm = BinM()
        params = {'binm': self.binm}
        self.urls = [
            ("/", REST.LandingHandler),
            ("/history/get", REST.HistoryGetHandler, params),
            ("/currencies/get", REST.CurrenciesGetHandler, params),
            ("/currencies/update", REST.CurrenciesUpdateHandler, params),
            ("/currencies/subscribe", REST.CurrenciesSubscribeHandler, ),
            ("/rates/get", REST.RatesGetHandler, params),
            ("/rates/subscribe", REST.RatesSubscribeHandler, ),
            ("/user/associate", REST.UserAssociateHandler, ),
            ("/user/subscribes/get", REST.UserSubscribesGetHandler, ),
            ("/user/subscribes/unsubscribe", REST.UserUnsubscribeHandler, ),
        ]
        self.application = Application(self.urls)
        self.application.listen(8080)

    def start(self):
        io_loop = IOLoop.current()
        io_loop.start()
