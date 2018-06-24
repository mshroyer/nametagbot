import os
import shutil
import tempfile
import unittest

from nametagbot import User
from nametagbot.db import Database


class DbTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test.db')
        self.db = Database(self.test_file)

    def tearDown(self):
        self.db.close()
        shutil.rmtree(self.test_dir)

    def test_reopen(self):
        self.db.close()

        # We should not fail to open the database a second time, even
        # though the tables have already been created.
        self.db = Database(self.test_file)

    def test_set_user_attendance(self):
        bob = User('1', 'Bob', 'avatar1')
        jay = User('2', 'Jay', 'avatar2')
        cara = User('3', 'Cara', 'avatar3')

        self.db.set_user_attendance(bob, True)
        self.db.set_user_attendance(jay, True)
        self.db.set_user_attendance(cara, False)
        self.assertListEqual(list(self.db.attending_users()), [bob, jay])

    def test_attending_users_sorted_by_nick(self):
        steve = User('1', 'Steve', 'avatar1')
        jay = User('2', 'Jay', 'avatar2')
        bob = User('3', 'Bob', 'avatar3')
        evan = User('4', 'Evan', 'avatar4')
        cara = User('5', 'Cara', 'avatar5')
        for user in [steve, jay, bob, evan, cara]:
            self.db.set_user_attendance(user, True)

        self.assertListEqual(
            list(self.db.attending_users()), [bob, cara, evan, jay, steve])

    def test_update_roster_preserves_attendance(self):
        bob = User('1', 'Bob', 'avatar1')
        self.db.set_user_attendance(bob, True)

        bob2 = bob._replace(avatar='avatar2')
        self.db.update_roster([bob2])
        self.assertListEqual(list(self.db.attending_users()), [bob2])

        self.db.set_user_attendance(bob, False)
        bob3 = bob2._replace(nick='Robert')
        self.db.update_roster([bob3])
        self.assertListEqual(list(self.db.attending_users()), [])

    def test_update_roster_does_not_remove_users(self):
        evan = User('1', 'Evan', 'avatar1')
        steve = User('2', 'Steve', 'avatar2')
        self.db.set_user_attendance(evan, True)
        self.db.set_user_attendance(steve, True)

        self.db.update_roster([evan])
        self.assertListEqual(list(self.db.attending_users()), [evan, steve])

    def test_update_roster_accepts_unknown_users(self):
        user1 = User('1', 'Bob', 'avatar1')
        self.db.update_roster([user1])
