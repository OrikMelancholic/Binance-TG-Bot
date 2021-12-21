import sqlite3
import sys
sys.path.append('..')

from Utilities import Logger


class DatabaseManager:
    def _createTables(self):
        tables = (
            (
                'Users(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, tid INTEGER NOT NULL UNIQUE)'
            ),
            (
                'Currencies(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, usdvalue FLOAT, flair TEXT UNIQUE, '
                'last_event DATETIME DEFAULT CURRENT_TIMESTAMP)'
            ),
            (
                'SubscriptionsCoin(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, uid INTEGER, cid INTEGER, '
                'last_event DATETIME DEFAULT CURRENT_TIMESTAMP, active BOOLEAN DEFAULT 1, '
                'FOREIGN KEY(uid) REFERENCES Users(id), '
                'FOREIGN KEY(cid) REFERENCES Currencies(id))'
            ),
            (
                'SubscriptionsRate(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, uid INTEGER, '
                'cid_from INTEGER, cid_to INTEGER, '
                'last_event DATETIME DEFAULT CURRENT_TIMESTAMP, active BOOLEAN DEFAULT 1, '
                'FOREIGN KEY(uid) REFERENCES Users(id), '
                'FOREIGN KEY(cid_to) REFERENCES Currencies(id), '
                'FOREIGN KEY(cid_from) REFERENCES Currencies(id))'
            )
        )

        for table in tables:
            try:
                cursor = self.connection.cursor()
                cursor.execute('CREATE TABLE IF NOT EXISTS %s;' % table)
            except sqlite3.Error as e:
                self.logger.error('Caught error %s' % e)

    def __init__(self):
        try:
            self.connection = sqlite3.connect('./DatabaseManager/backend.db')
            self.logger = Logger('DBM')
            self._createTables()
        except sqlite3.Error as e:
            self.logger.critical('Caught error %s' % e)
            sys.exit(1)

    def _select(self, table, what='*', where=None):
        try:
            sql = 'SELECT %s FROM %s' % (what, table)
            if where:
                sql += ' WHERE %s' % where
            cursor = self.connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            self.logger.error('Caught error %s' % e)
            return None

    def _insert(self, table, data):
        try:
            sql = 'INSERT INTO %s VALUES (%s)' % (table, ','.join(['?' for _ in data]))
            cursor = self.connection.cursor()
            cursor.execute(sql, data)
            self.connection.commit()
        except sqlite3.Error as e:
            self.logger.error('Caught error %s' % e)

    def _update(self, table, set, where):
        try:
            sql = 'UPDATE %s SET %s WHERE %s' % (table, set, where)
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
        except sqlite3.Error as e:
            self.logger.error('Caught error %s' % e)

    def getUser(self, tid=None):
        rows = None
        if tid:
            self.logger.log('Selecting user with tid %s' % tid)
            rows = self._select('Users', where='tid=%s' % tid)
            rows = rows[0] if rows else rows
        else:
            self.logger.log('Selecting all users')
            rows = self._select('Users')
        self.logger.log('Returning %s' % self.logger.fancy_json(rows))
        return rows

    def addUser(self, tid):
        self.logger.log('Adding user %s to the Database' % tid)
        self._insert('Users(tid)', (tid,))
        row = self.getUser(tid)
        return row

    def getCurrency(self, flair=None):
        rows = None
        if flair:
            self.logger.log('Selecting currency with flair %s' % flair)
            rows = self._select('Currencies', where='flair=\'%s\'' % flair)
            rows = rows[0] if rows else rows
        else:
            self.logger.log('Selecting all currencies')
            rows = self._select('Currencies')
        self.logger.log('Returning %s' % self.logger.fancy_json(rows))
        return rows

    def addCurrency(self, flair, usdvalue=0):
        self.logger.log('Adding currency %s to the Database' % flair)
        self._insert('Currencies(flair, usdvalue)', (flair, usdvalue))
        row = self.getCurrency(flair)
        return row

    def updateCurrency(self, flair, usdvalue):
        self.logger.log('Updating currency %s with value %s' % (flair, usdvalue))
        self._update('Currencies', 'usdvalue=%s,last_event=CURRENT_TIMESTAMP' % usdvalue, 'flair=\'%s\'' % flair)
        row = self.getCurrency(flair)
        return row

    def getCurrencySubscription(self, tid=None, flair=None):
        what = 'SubscriptionsCoin.*'
        table = 'SubscriptionsCoin LEFT JOIN Currencies C on SubscriptionsCoin.cid = C.id ' \
                'LEFT JOIN Users U on SubscriptionsCoin.uid = U.id'
        where = []
        if tid:
            where += ['tid=%s' % tid]
        if flair:
            where += ['flair=\'%s\'' % flair]
        where = ' AND '.join(where)
        self.logger.log('Selecting SubscriptionsCoin with where \'%s\'' % where)
        rows = self._select(table, what, where)
        if tid and flair and rows:
            rows = rows[0]
        self.logger.log('Returning %s' % self.logger.fancy_json(rows))
        return rows

    def addCurrencySubscription(self, tid, flair):
        self.logger.log('Adding SubscriptionsCoin with tid %s and flair %s to the Database' % (tid, flair))
        test = self.getCurrencySubscription(tid, flair)
        if test:
            self.logger.log('There is already SubscriptionsCoin with tid %s and flair %s in the Database!' % (tid, flair))
            return test
        uid = self.getUser(tid)[0]
        cid = self.getCurrency(flair)[0]
        if uid and cid:
            self._insert('SubscriptionsCoin(uid, cid)', (uid, cid))
            rows = self.getCurrencySubscription(tid, flair)
            return rows
        else:
            return None

    def updateCurrencySubscription(self, tid, flair, active):
        self.logger.log('Updating SubscriptionsCoin tid %s flair %s with value %s' % (tid, flair, active))
        uid = self.getUser(tid)[0]
        cid = self.getCurrency(flair)[0]
        if uid and cid:
            self._update(
                'SubscriptionsCoin', 'active=%s,last_event=CURRENT_TIMESTAMP' % int(active),
                'uid=%s AND cid=%s' % (uid, cid)
            )
        row = self.getCurrencySubscription(tid, flair)
        return row

    def getRateSubscription(self, tid=None, flair_from=None, flair_to=None):
        what = 'SubscriptionsRate.*, (C_from.usdvalue / C_to.usdvalue) as rate'
        table = 'SubscriptionsRate LEFT JOIN Currencies C_to on SubscriptionsRate.cid_to = C_to.id ' \
                'LEFT JOIN Currencies C_from on SubscriptionsRate.cid_from = C_from.id ' \
                'LEFT JOIN Users U on SubscriptionsRate.uid = U.id'
        where = []
        if tid:
            where += ['tid=%s' % tid]
        if flair_from:
            where += ['flair_from=\'%s\'' % flair_from]
        if flair_to:
            where += ['flair_to=\'%s\'' % flair_to]
        where = ' AND '.join(where)
        self.logger.log('Selecting SubscriptionsRate with where \'%s\'' % where)
        rows = self._select(table, what, where)
        if tid and flair_from and flair_to and rows:
            rows = rows[0]
        self.logger.log('Returning %s' % self.logger.fancy_json(rows))
        return rows

    def addRateSubscription(self, tid, flair_from, flair_to):
        self.logger.log('Adding SubscriptionsRate with tid %s, flair_from %s and flair_to %s to the Database'
                        % (tid, flair_from, flair_to))
        test = self.getRateSubscription(tid, flair_from, flair_to)
        if test:
            self.logger.log('There is already SubscriptionsRate with tid %s, flair_from %s and flair_to %s in the Database!'
                            % (tid, flair_from, flair_to))
            return test
        uid = self.getUser(tid)[0]
        cid_from = self.getCurrency(flair_from)[0]
        cid_to = self.getCurrency(flair_to)[0]
        if uid and cid_from and cid_to:
            self._insert('SubscriptionsRate(uid, cid_from, cid_to)', (uid, cid_from, cid_from))
            rows = self.getRateSubscription(tid, flair_from, flair_to)
            return rows
        else:
            return None

    def updateRateSubscription(self, tid, flair_from, flair_to, active):
        self.logger.log('Updating SubscriptionsCoin tid %s, flair_from %s and flair_to %s with value %s'
                        % (tid, flair_from, flair_to, active))
        uid = self.getUser(tid)[0]
        cid_from = self.getCurrency(flair_from)[0]
        cid_to = self.getCurrency(flair_to)[0]
        if uid and cid_from and cid_to:
            self._update(
                'SubscriptionsCoin', 'active=%s,last_event=CURRENT_TIMESTAMP' % int(active),
                                     'uid=%s AND cid_from=%s AND cid_to=%s' % (uid, cid_from, cid_to)
            )
        row = self.getRateSubscription(tid, flair_from, flair_to)
        return row
