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
            self.conn.execute(
                '''
                UPDATE Users SET attending = ? WHERE user_id = ?
            ''', (is_attending, user.user_id))

    def update_roster(self, users):
        """Updates the roster with the users' nicks and avatars."""
        with self.conn:
            self.conn.execute('BEGIN')
            for user in users:
                self._upsert_user(user)

    def attending_users(self):
        cur = self.conn.cursor()
        cur.execute(
            'SELECT user_id, nick, avatar FROM Users WHERE attending = TRUE;')

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
            INSERT INTO Users (user_id, nick, avatar) VALUES (?, ?, ?)
            ON CONFLICT (user_id) DO UPDATE SET
                nick = excluded.nick,
                avatar = excluded.avatar;
        ''', tuple(user))

    def _init_db(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS Users
                (user_id TEXT NOT NULL,
                 nick TEXT,
                 avatar TEXT,
                 attending BOOL,
                 PRIMARY KEY (user_id));
        ''')
        self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_attending_nick
            ON Users (attending, nick);
        ''')
