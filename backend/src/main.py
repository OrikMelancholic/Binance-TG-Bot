from DatabaseManager import DatabaseManager as DBM
from BinanceManager import BinanceManager as BinM
from MainManager import MainManager as MainM

from tornado.ioloop import IOLoop


if __name__ == "__main__":
    #dbm = DBM()
    # dbm.addUser(1337)
    # dbm.addUser(1338)
    # dbm.getUser()
    # user = dbm.getUser(1337)
    # dbm.addCurrency('BTC', 100)
    # dbm.addCurrency('SHIB', 100)
    # dbm.updateCurrency('BTC', 200)
    # coin = dbm.getCurrency('BTC')
    # dbm.addCurrencySubscription(1337, 'BTC')
    # dbm.getCurrencySubscription(flair='BTC')
    # dbm.updateCurrencySubscription(1337, 'BTC', True)
    # dbm.addRateSubscription(1337, 'BTC', 'SHIB')

    #binm = BinM()
    #binm.getUsdValue('BTC')

    mainm = MainM()
    IOLoop.instance().start()
