import sys
sys.path.append('..')

from Utilities import Logger
from BinanceManager import BinanceManager as BinM
import REST

from tornado.web import Application


class MainManager:
    def __init__(self):
        self.logger = Logger('MainM')
        self.urls = [
            ("/", REST.LandingHandler),
            ("/history/get", REST.HistoryGetHandler),
            ("/currencies/get", REST.CurrenciesGetHandler),
            ("/currencies/update", REST.CurrenciesUpdateHandler),
            ("/currencies/subscribe", REST.CurrenciesSubscribeHandler),
            ("/rates/get", REST.RatesGetHandler),
            ("/rates/subscribe", REST.RatesSubscribeHandler),
            ("/user/associate", REST.UserAssociateHandler),
            ("/user/subscribes/get", REST.UserSubscribesGetHandler),
            ("/user/subscribes/unsubscribe", REST.UserUnsubscribeHandler),
        ]
        self.application = Application(self.urls)
        self.application.listen(8080)
