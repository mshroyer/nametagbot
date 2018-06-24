import sqlite3

from nametagbot import User

__all__ = ['Database']


class Database:
    """Database interface.

    Not threadsafe.

    """

    def __init__(self, db_path):
        self.conn = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES,
            isolation_level=None,  # Explicit transaction handling.
            check_same_thread=True)
        self._init_db()

    def set_user_attendance(self, user, is_attending):
        with self.conn:
            self.conn.execute('BEGIN')
            self._upsert_user(user)

            if is_attending:
                query = 'INSERT OR IGNORE INTO Attendance VALUES (?);'
            else:
                query = 'DELETE FROM Attendance WHERE user_id = ?;'

            self.conn.execute(query, (user.user_id))

    def update_roster(self, users):
        """Updates the roster with the users' nicks and avatars."""
        with self.conn:
            self.conn.execute('BEGIN')
            for user in users:
                self._upsert_user(user)

    def attending_users(self):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT user_id, nick, avatar
            FROM Attendance NATURAL LEFT JOIN User
            ORDER BY nick;
        ''')

        while True:
            rows = cur.fetchmany()
            if not rows:
                break
            for row in rows:
                yield User(*row)

        cur.close()

    def close(self):
        self.conn.close()

    def _upsert_user(self, user):
        self.conn.execute(
            '''
            INSERT OR REPLACE INTO User (user_id, nick, avatar)
            VALUES (?, ?, ?);
        ''', tuple(user))

    def _init_db(self):
        # It's easy to implement _upsert_user with a single table using
        # Sqlite 3.24's "ON CONFLICT ... DO UPDATE" syntax, but this way
        # the program won't require a Python built against the very latest
        # sqlite3.
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS User
                (user_id TEXT NOT NULL,
                 nick TEXT,
                 avatar TEXT,
                 PRIMARY KEY (user_id));
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS Attendance
                (user_id TEXT NOT NULL UNIQUE,
                 FOREIGN KEY (user_id) REFERENCES User (user_id));
        ''')
