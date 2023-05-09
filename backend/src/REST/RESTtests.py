import builtins
import unittest
from unittest.mock import MagicMock, patch
from backend.src.Utilities import Logger
from backend.src.REST import BinanceHandler, TeapotHandler, AuthHandler

_trusted_token = '03e2042c9fd8f6cdb946ddb123576736defff6ed1859cdce9ef6b34b008a97b9'
_logger = Logger('REST')
class TestBinanceHandler(unittest.TestCase):
    def setUp(self):
        self.binm = MagicMock()
        self.handler = BinanceHandler()
        self.handler.initialize(self.binm)

    def test_bin_manager_call(self):
        method = MagicMock()
        data_in = {'arg1': 'value1', 'arg2': 'value2'}
        expected_data_out = {'out1': 'value3', 'out2': 'value4'}
        method.return_value = expected_data_out

        with patch.object(_logger, 'log') as mock_logger:
            with patch.object(builtins, 'response') as mock_response:
                self.handler.bin_manager_call('handler_name', method, data_in)

                self.assertEqual(mock_logger.call_count, 2)
                mock_logger.assert_any_call('handler_name:\n%s' % _logger.fancy_json(data_in))
                mock_logger.assert_any_call('Returning:\n%s' % _logger.fancy_json(expected_data_out))

                mock_response.assert_called_once_with(self.handler, expected_data_out)

class TestTeapotHandler(unittest.TestCase):
    def setUp(self):
        self.handler = TeapotHandler()

    def test_get(self):
        with patch.object(builtins, 'response') as mock_response:
            self.handler.get()
            mock_response.assert_called_once_with(self.handler, {'response': 'Я чайничек.'}, 418)

class TestAuthHandler(unittest.TestCase):
    def setUp(self):
        self.binm = MagicMock()
        self.handler = AuthHandler()
        self.handler.initialize(self.binm)

    def test_prepare_missing_token(self):
        with patch.object(builtins, 'response') as mock_response:
            self.handler.get()
            mock_response.assert_called_once_with(self.handler, 'Необходима авторизация.', 400)
            self.handler.finish.assert_called_once()

    def test_prepare_invalid_token(self):
        token = 'invalid_token'
        with patch.object(builtins, 'response') as mock_response:
            self.handler.get(token=token)
            mock_response.assert_called_once_with(self.handler, 'Неактивный токен.', 401)
            self.handler.finish.assert_called_once()

    def test_prepare_valid_token(self):
        token = _trusted_token
        with patch.object(builtins, 'response') as mock_response:
            self.handler.get(token=token)
            mock_response.assert_not_called()
