import sys
sys.path.append('..')

import tornado.gen
import tornado.web
from tornado.websocket import WebSocketHandler
from backend.src.Utilities import Logger
from backend.src.REST import response
from backend.src.REST import _trusted_token

_logger = Logger('Sock')


class PushWebSockets(WebSocketHandler):
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

    def initialize(self, io_loop, binm):
        self.binm = binm
        self.io_loop = io_loop
        self.arm_message()

    def arm_message(self):
        _logger.log('Tripped message mine')
        self.io_loop.add_future(self.binm.push_stack, self.send_messages)

    def send_messages(self, messages):
        messages = messages.result()
        _logger.log('Sending messages %s' % messages)
        for message in messages:
            self.write_message(message)
        self.io_loop.call_later(5, self.arm_message)

    def open(self):
        _logger.log('Opened new websocket connection')

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        _logger.log('Websocket closed')
