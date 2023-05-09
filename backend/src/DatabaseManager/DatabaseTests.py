import unittest
from unittest.mock import MagicMock
import sqlite3

from backend.src.DatabaseManager import DatabaseManager


class TestCreateTables(unittest.TestCase):

    def __init__(self, methodName: str = ...):
        super().__init__(methodName)
        self.logger = None

    def setUp(self):
        self.connection = sqlite3.connect(':memory:')

    def tearDown(self):
        self.connection.close()

    def test_create_tables(self):
        self._createTables()

        cursor = self.connection.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = cursor.fetchall()
        self.assertIn(('Users',), tables)
        self.assertIn(('Currencies',), tables)
        self.assertIn(('SubscriptionsCoin',), tables)

    def _createTables(self):
        tables = (
            (
                'Users(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, tid INTEGER NOT NULL UNIQUE)'
            ),
            (
                'Currencies(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, usdvalue FLOAT NOT NULL, '
                'flair TEXT UNIQUE NOT NULL, last_event DATETIME DEFAULT CURRENT_TIMESTAMP)'
            ),
            (
                'SubscriptionsCoin(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, '
                'uid INTEGER NOT NULL, cid INTEGER NOT NULL, '
                'target FLOAT, last_event DATETIME DEFAULT CURRENT_TIMESTAMP, active BOOLEAN DEFAULT 1, '
                'FOREIGN KEY(uid) REFERENCES Users(id), '
                'FOREIGN KEY(cid) REFERENCES Currencies(id))'
            ),
        )

        for table in tables:
            try:
                cursor = self.connection.cursor()
                cursor.execute('CREATE TABLE IF NOT EXISTS %s;' % table)
            except sqlite3.Error as e:
                self.logger.error('Caught error %s' % e)

class TestDatabaseManager(unittest.TestCase):

    db = DatabaseManager()

    @classmethod
    def test_addCurrencySubscription_success(self):
        tid = 123
        flair = 'USD'
        result = self.db.addCurrencySubscription(tid, flair)
        expected = [(1, 1, None)]
        self.assertEqual(result, expected)

    def test_addCurrencySubscription_already_exists(self):
        tid = 123
        flair = 'USD'
        self.db._select = MagicMock(return_value=[(1, 1, None)])
        result = self.db.addCurrencySubscription(tid, flair)
        expected = (1, 1, None)
        self.assertEqual(result, expected)

    def test_addCurrencySubscription_invalid_input(self):
        tid = 123
        flair = 'invalid_flair'
        self.db.getUser = MagicMock(return_value=[])
        result = self.db.addCurrencySubscription(tid, flair)
        expected = []
        self.assertEqual(result, expected)

    def test_updateCurrencySubscription_success(self):
        tid = 123
        flair = 'USD'
        target = 100
        active = 1
        self.db.getUser = MagicMock(return_value=[1])
        self.db.getCurrency = MagicMock(return_value=[1])
        self.db.getCurrencySubscription = MagicMock(return_value=[(1, 1, None)])
        self.db._update = MagicMock(return_value=None)
        result = self.db.updateCurrencySubscription(tid, flair, target, active)
        expected = [(1, 1, None)]
        self.assertEqual(result, expected)

    def test_updateCurrencySubscription_invalid_input(self):
        tid = 123
        flair = 'invalid_flair'
        self.db.getUser = MagicMock(return_value=[])
        self.db.getCurrency = MagicMock(return_value=[])
        self.db.getCurrencySubscription = MagicMock(return_value=[])
        result = self.db.updateCurrencySubscription(tid, flair)
        expected = []
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()


# import unittest
# from backend.src.DatabaseManager import DatabaseManager
#
#
# class TestDatabaseManager(unittest.TestCase):
#
#     def setUp(self):
#         self.db = DatabaseManager()
#
#     def test_getUser(self):
#         tid = 123
#         self.db.addUser(tid)
#         rows = self.db.getUser(tid)
#         self.assertIsNotNone(rows)
#         self.assertEqual(rows[0]['tid'], tid)
#
#     def test_addUser(self):
#         tid = 456
#         row = self.db.addUser(tid)
#         self.assertEqual(row[1], tid)
#
#     def test_getCurrency(self):
#         flair = 'BTC'
#         self.db.addCurrency(flair)
#         rows = self.db.getCurrency(flair)
#         self.assertEqual(rows[0], 1)
#
#     def test_addCurrency(self):
#         flair = 'ETH'
#         usdvalue = 2000
#         row = self.db.addCurrency(flair, usdvalue)
#         self.assertEqual(row[1], usdvalue)
#         self.assertEqual(row[2], flair)
#
#
#     def test_updateCurrency(self):
#         flair = 'ETH'
#         usdvalue = 2500
#         self.db.addCurrency(flair)
#         self.db.updateCurrency(flair, usdvalue)
#         rows = self.db.getCurrency(flair)
#         self.assertEqual(rows[2], usdvalue)
#
#     def test_getCurrencySubscription(self):
#         uid = 678
#         cid = 2932
#         self.db.addCurrencySubscription(uid, cid)
#         rows = self.db.getCurrencySubscription(uid, cid)
#         self.assertEqual(rows[0], uid)
#
#     def test_addCurrencySubscription(self):
#         uid = 678
#         cid = 2932
#         target = 3000
#         row = self.db.addCurrencySubscription(uid, cid, target)
#         self.assertEqual(row[1], uid)
#         self.assertEqual(row[2], cid)
#         self.assertEqual(row[3], target)
#
#
# if __name__ == '__main__':
#     unittest.main()
