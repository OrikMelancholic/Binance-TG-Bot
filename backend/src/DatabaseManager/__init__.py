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
            self.logger.log(sql)
            if where:
                sql += ' WHERE %s' % where
            cursor = self.connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            self.logger.log(self.logger.fancy_json(rows))
            return rows
        except sqlite3.Error as e:
            self.logger.error('Caught error %s' % e)
            return None

    def _insert(self, table, data):
        try:
            sql = 'INSERT INTO %s VALUES (%s)' % (table, ','.join(['?' for _ in data]))
            self.logger.log(sql)
            cursor = self.connection.cursor()
            cursor.execute(sql, data)
            self.connection.commit()
        except sqlite3.Error as e:
            self.logger.error('Caught error %s' % e)

    def _update(self, table, set, where):
        try:
            sql = 'UPDATE %s SET %s WHERE %s' % (table, set, where)
            self.logger.log(sql)
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
        except sqlite3.Error as e:
            self.logger.error('Caught error %s' % e)

    def getUser(self, tid=None):
        if tid:
            rows = self._select('Users', where='tid=%s' % tid)
            rows = rows[0] if rows else rows
        else:
            rows = self._select('Users')
        return rows

    def addUser(self, tid):
        self._insert('Users(tid)', (tid,))
        row = self.getUser(tid)
        return row

    def getCurrency(self, flair=None):
        if flair:
            rows = self._select('Currencies', where='flair=\'%s\'' % flair)
            rows = rows[0] if rows else rows
        else:
            rows = self._select('Currencies')
        self.logger.log('Returning %s' % self.logger.fancy_json(rows))
        return rows

    def addCurrency(self, flair, usdvalue=0):
        self._insert('Currencies(flair, usdvalue)', (flair, usdvalue))
        row = self.getCurrency(flair)
        return row

    def updateCurrency(self, flair, usdvalue):
        self._update('Currencies', 'usdvalue=%s,last_event=CURRENT_TIMESTAMP' % usdvalue, 'flair=\'%s\'' % flair)
        row = self.getCurrency(flair)
        return row

    def getCurrencySubscription(self, tid=None, flair=None, active=None):
        what = '*'
        table = 'SubscriptionsCoin LEFT JOIN Currencies C on SubscriptionsCoin.cid = C.id ' \
                'LEFT JOIN Users U on SubscriptionsCoin.uid = U.id'
        where =[]
        if tid:
            where += ['tid=%s' % tid]
        if flair:
            where += ['flair=\'%s\'' % flair]
        if active is not None:
            where += ['active=%s' % active]
        where = ' AND '.join(where)
        rows = self._select(table, what, where)
        if tid and flair and rows:
            rows = rows[0]
        return rows

    def addCurrencySubscription(self, tid, flair, target=None):
        test = self.getCurrencySubscription(tid, flair)
        if test:
            return test
        try:
            uid = self.getUser(tid)[0]
            cid = self.getCurrency(flair)[0]
        except IndexError:
            return []
        if uid and cid:
            self._insert('SubscriptionsCoin(uid, cid, target)', (uid, cid, target))
            rows = self.getCurrencySubscription(tid, flair)
            return rows
        else:
            return None

    def updateCurrencySubscription(self, tid, flair, target=None, active=None):
        self.logger.log('Updating SubscriptionsCoin tid %s flair %s with value %s (active: %s)' % (tid, flair, target, active))
        try:
            uid = self.getUser(tid)[0]
            cid = self.getCurrency(flair)[0]
        except IndexError:
            return []
        upd = ['last_event=CURRENT_TIMESTAMP']
        if target:
            upd += ['target=%s' % target]
        else:
            upd += ['target=NULL']
        if active is not None:
            upd += ['active=%s' % active]
        upd = ','.join(upd)
        if uid and cid:
            self._update('SubscriptionsCoin', upd, 'uid=%s AND cid=%s' % (uid, cid))
        row = self.getCurrencySubscription(tid, flair)
        return row
