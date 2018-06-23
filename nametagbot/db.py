import sqlite3

from nametagbot import User


class Database:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def set_user_attendance(self, user, is_attending):
        with self.conn:
            self._update_user(user)
            self.conn.execute(
                r'''
                UPDATE Users SET attending = ? WHERE user_id = ?
            ''', (is_attending, user.user_id))

    def update_roster(self, users):
        """Updates the roster with the users' nicks and avatars."""
        with self.conn:
            for user in users:
                self._update_user(user)

    def attending_users(self):
        cur = self.conn.cursor()
        cur.execute(
            r'SELECT user_id, nick, avatar FROM Users WHERE attending;')

        while True:
            rows = cur.fetchmany()
            if not rows:
                break
            for row in rows:
                yield User(*row)

        cur.close()

    def _update_user(self, user):
        self.conn.execute(
            r'''
            INSERT INTO Users (user_id, nick, avatar) VALUES (?, ?, ?)
            ON CONFLICT (user_id) DO UPDATE SET
                nick = excluded.nick,
                avatar = excluded.avatar;
        ''', (user.user_id, user.nick, user.avatar))

    def _init_db(self):
        with self.conn:
            self.conn.execute(r'''
                CREATE TABLE IF NOT EXISTS Users
                    (user_id STRING NOT NULL,
                     nick STRING,
                     avatar STRING,
                     attending BOOL,
                     PRIMARY KEY (user_id));
            ''')
            self.conn.execute(r'''
                CREATE INDEX IF NOT EXISTS idx_attending ON Users (attending);
            ''')
