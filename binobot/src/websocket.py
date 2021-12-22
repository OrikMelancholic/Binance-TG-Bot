from tornado.ioloop import IOLoop
from tornado import gen
from tornado.websocket import websocket_connect


class Client(object):
    def __init__(self, websocket_url):
        self.url = websocket_url
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.connect()
        self.ioloop.start()

    @gen.coroutine
    def connect(self):
        print("Попытка подключения")
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception:
            print("Ошибка подключения")
        else:
            print("Подключено")
            self.run()

    @gen.coroutine
    def run(self):
        while True:
            msg = yield self.ws.read_message()
            if msg is None:
                print("Подключение закрыто")
                self.ws = None
                break

