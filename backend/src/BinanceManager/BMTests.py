import unittest
import tornado.ioloop
from binance.client import Client
from backend.src.BinanceManager import BinanceManager


class TestBinanceManager(unittest.TestCase):
    def setUp(self):
        self.loop = tornado.ioloop.IOLoop.current()
        self.bm = BinanceManager(io_loop=self.loop)

    def test_init(self):
        self.assertIsInstance(self.bm, BinanceManager)
        self.assertIsInstance(self.bm.client, Client)
        self.assertEqual(self.bm.push_stack.result(), None)
        self.assertEqual(self.bm.push_stack_delta.seconds, 30)

if __name__ == '__main__':
    unittest.main()
