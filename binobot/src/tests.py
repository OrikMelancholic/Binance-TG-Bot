import asyncio
from unittest import mock, TestCase

from binobot.src.websocket import WebSocket


class TestWebSocket(TestCase):
    def setUp(self):
        self.websocket_url = 'ws://test.com'
        self.bot = mock.Mock()
        self.websocket = WebSocket(self.websocket_url, self.bot)

    def tearDown(self):
        self.websocket.stop()

    def test_connect(self):
        with mock.patch('my_module.websockets.connect') as mock_connect:
            self.websocket.connect()
            mock_connect.assert_called_with(self.websocket_url, loop=self.websocket._loop)

    def test_disconnect(self):
        with mock.patch('my_module.websockets.connect'):
            self.websocket.connect()

        with mock.patch('my_module.asyncio.sleep') as mock_sleep:
            self.websocket.disconnect()
            mock_sleep.assert_called_with(2, loop=self.websocket._loop)

    def test_listen(self):
        with mock.patch('my_module.websockets.connect') as mock_connect:
            mock_ws = mock_connect.return_value.__aenter__.return_value
            mock_ws.open = True
            mock_packet = {'flair': 'btc', 'target': 100, 'price': 99, 'rising': True, 'user_id': 123}
            mock_ws.recv.return_value = asyncio.Future()
            mock_ws.recv.return_value.set_result(mock_packet)
            self.websocket.connect()

            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.sleep(0.1))

            self.bot.send_message.assert_called_with(
                chat_id=mock_packet['user_id'],
                text='Валюта %s прошла цель в %s$ с курсом %s$ (%s)' % (
                    mock_packet['flair'], mock_packet['target'], mock_packet['price'], 'рост' if mock_packet['rising'] else 'падение'
                )
            )
