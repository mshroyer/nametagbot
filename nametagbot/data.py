# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import logging
import os
import requests
import shutil
import sqlite3

from nametagbot import User

__all__ = ['AvatarCache', 'Roster']

CDN_PREFIX = 'https://cdn.discordapp.com/'


class Roster:
    """Roster database interface.

    Not threadsafe.

    """

    def __init__(self, db_path, init_db=True):
        _makedirs_for_data_file(db_path)
        self.db = sqlite3.connect(
            db_path,
            isolation_level=None,  # Explicit transaction handling.
            check_same_thread=True)
        if init_db:
            self._init_db()

    def set_user_attendance(self, user, is_attending):
        with _Transaction(self.db):
            self._upsert_user(user)

            if is_attending:
                query = '''
                    INSERT OR IGNORE INTO Attendance (user_id)
                    VALUES (?);
                '''
            else:
                query = 'DELETE FROM Attendance WHERE user_id = ?;'

            self.db.execute(query, (user.user_id))

    def update_users(self, users):
        """Updates the roster with the users' nicks and avatars."""
        with _Transaction(self.db):
            for user in users:
                self._upsert_user(user)

    def attending_users(self):
        cur = self.db.cursor()
        cur.execute('''
            SELECT user_id, nick, discriminator, avatar
            FROM Attendance NATURAL LEFT JOIN User
            ORDER BY nick COLLATE NOCASE ASC;
        ''')

        while True:
            rows = cur.fetchmany()
            if not rows:
                break
            for row in rows:
                yield User(*row)

        cur.close()

    def close(self):
        self.db.close()

    def _upsert_user(self, user):
        self.db.execute(
            '''
            INSERT OR REPLACE INTO User (user_id, nick, discriminator, avatar)
            VALUES (?, ?, ?, ?);
        ''', tuple(user))

    def _init_db(self):
        # It's easy to implement _upsert_user with a single table using
        # Sqlite 3.24's "ON CONFLICT ... DO UPDATE" syntax, but this way
        # the program won't require a Python built against the very latest
        # sqlite3.
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS User
                (user_id TEXT NOT NULL,
                 nick TEXT,
                 discriminator TEXT,
                 avatar TEXT,
                 PRIMARY KEY (user_id));
        ''')
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS Attendance
                (user_id TEXT NOT NULL UNIQUE,
                 FOREIGN KEY (user_id) REFERENCES User (user_id));
        ''')

    def __enter__(self):
        pass

    def __exit__(self, type, value, tb):
        self.close()


class AvatarCache:
    """Loading cache of user avatars."""

    def __init__(self, cache_path):
        self.cache_path = cache_path
        _makedirs(cache_path)

    def get_avatar(self, user, path):
        self._cache_avatar(user)
        shutil.copyfile(self._avatar_cache_path(user), path)

    def _cache_avatar(self, user):
        cache_path = self._avatar_cache_path(user)
        if os.path.exists(cache_path):
            logging.debug('Avatar cache hit at %s', cache_path)
            return

        resp = requests.get(self._avatar_url(user))
        if not resp.ok:
            if resp.status_code == 404:
                raise ValueError('Invalid avatar: {}'.format(resp.reason))
            else:
                raise Exception('Error getting avatar: {}'.format(resp.reason))

        content_type = resp.headers['Content-Type']
        if content_type != 'image/png':
            raise ValueError(
                'Unexpected avatar content type {}'.format(content_type))

        with open(cache_path, 'wb') as f:
            f.truncate()
            f.write(resp.content)

        logging.debug('Cached new avatar at %s', cache_path)

    def _avatar_cache_path(self, user):
        if user.avatar:
            return os.path.join(
                self.cache_path,
                '{user_id}_{avatar}.png'.format(**user._asdict()))
        else:
            return os.path.join(
                self.cache_path, 'default_{}.png'.format(
                    self._default_avatar(user)))

    @staticmethod
    def _default_avatar(user):
        try:
            return str(int(user.discriminator) % 5)
        except ValueError:
            return '0'

    @classmethod
    def _avatar_url(klass, user):
        if user.avatar:
            return CDN_PREFIX + 'avatars/{user_id}/{avatar}.png'.format(
                **user._asdict())
        else:
            return CDN_PREFIX + 'embed/avatars/{}.png'.format(
                klass._default_avatar(user))


class _Transaction:
    """Transaction context manager.

    The Python sqlite3 module handles transactions in a counter-intuitive
    way.  Among other issues, the database connection can be used as a
    context manager that automatically commits or rolls back transactions,
    however it does not automatically begin a connection.  This class wraps
    the connection's context manager to automatically execute BEGIN when
    entering.

    """

    def __init__(self, db, kind='DEFERRED'):
        self.db = db
        self.kind = kind

    def __enter__(self):
        self.db.execute('BEGIN {}'.format(self.kind))

    def __exit__(self, *args):
        self.db.__exit__(*args)


def _makedirs(dir_path):
    os.makedirs(dir_path, 0o750, exist_ok=True)


def _makedirs_for_data_file(path):
    """Ensures that parent dirs exist for the given data file path."""
    _makedirs(os.path.dirname(os.path.abspath(path)))
