import os
import shutil
import tempfile
import unittest

from nametagbot import User
from nametagbot.db import Database


class DbTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db = Database(os.path.join(self.test_dir, 'test.db'))

    def tearDown(self):
        self.db.conn.close()
        shutil.rmtree(self.test_dir)

    def test_set_user_attendance(self):
        user = User('1', 'Bob', 'Avatar1')
        self.db.set_user_attendance(user, True)
        self.assertEqual(list(self.db.attending_users()), [user])

    def test_update_roster_preserves_attendance(self):
        self.db.set_user_attendance(User('1', 'Bob', 'avatar1'), True)
        self.db.update_roster([User('1', 'Bobby', 'avatar2')])

        self.assertEqual(
            list(self.db.attending_users()), [User('1', 'Bobby', 'avatar2')])
