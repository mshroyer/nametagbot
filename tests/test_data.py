import os
import shutil
import tempfile
import unittest

from nametagbot import User
from nametagbot.data import Roster


class RosterTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test.db')
        self.roster = Roster(self.test_file)

    def tearDown(self):
        self.roster.close()
        shutil.rmtree(self.test_dir)

    def test_reopen(self):
        self.roster.close()

        # We should not fail to open the roster a second time, even though
        # the tables have already been created.
        self.roster = Roster(self.test_file)

    def test_set_user_attendance(self):
        bob = User('1', 'Bob', 'avatar1')
        jay = User('2', 'Jay', 'avatar2')
        cara = User('3', 'Cara', 'avatar3')

        self.roster.set_user_attendance(bob, True)
        self.roster.set_user_attendance(jay, True)
        self.roster.set_user_attendance(cara, False)
        self.assertListEqual(list(self.roster.attending_users()), [bob, jay])

        self.roster.set_user_attendance(jay, False)
        self.roster.set_user_attendance(cara, True)
        self.assertListEqual(list(self.roster.attending_users()), [bob, cara])

    def test_set_user_attendance_updates_user(self):
        steve = User('1', 'Steve', 'avatar1')
        self.roster.set_user_attendance(steve, False)

        steve2 = steve._replace(avatar='avatar2')
        self.roster.set_user_attendance(steve2, True)

        self.assertListEqual(list(self.roster.attending_users()), [steve2])

    def test_attending_users_sorted_by_nick(self):
        steve = User('1', 'Steve', 'avatar1')
        jay = User('2', 'Jay', 'avatar2')
        bob = User('3', 'Bob', 'avatar3')
        evan = User('4', 'Evan', 'avatar4')
        cara = User('5', 'Cara', 'avatar5')
        for user in [steve, jay, bob, evan, cara]:
            self.roster.set_user_attendance(user, True)

        self.assertListEqual(
            list(self.roster.attending_users()), [bob, cara, evan, jay, steve])

    def test_update_users_preserves_attendance(self):
        bob = User('1', 'Bob', 'avatar1')
        self.roster.set_user_attendance(bob, True)

        bob2 = bob._replace(avatar='avatar2')
        self.roster.update_users([bob2])
        self.assertListEqual(list(self.roster.attending_users()), [bob2])

        self.roster.set_user_attendance(bob, False)
        bob3 = bob2._replace(nick='Robert')
        self.roster.update_users([bob3])
        self.assertListEqual(list(self.roster.attending_users()), [])

    def test_update_users_does_not_remove_users(self):
        evan = User('1', 'Evan', 'avatar1')
        steve = User('2', 'Steve', 'avatar2')
        self.roster.set_user_attendance(evan, True)
        self.roster.set_user_attendance(steve, True)

        self.roster.update_users([evan])
        self.assertListEqual(
            list(self.roster.attending_users()), [evan, steve])

    def test_update_users_accepts_unknown_users(self):
        user1 = User('1', 'Bob', 'avatar1')
        self.roster.update_users([user1])
