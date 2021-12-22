import logging

from DatabaseManager import DatabaseManager as DBM
from BinanceManager import BinanceManager as BinM
from MainManager import MainManager as MainM

from tornado.ioloop import IOLoop


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    mainm = MainM()
    mainm.start()