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

    def testSetUserAttendance(self):
        user = User('1', 'Bob', 'Avatar1')
        self.db.set_user_attendance(user, True)
        self.assertEqual(list(self.db.attending_users()), [user])
