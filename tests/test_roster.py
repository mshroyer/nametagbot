import os
import pytest

from nametagbot import User
from nametagbot.data import Roster


@pytest.fixture
def roster(tmpdir):
    r = Roster(os.path.join(tmpdir, 'roster.db'))
    yield r
    r.close()


def test_reopen(roster, tmpdir):
    roster.close()

    # We should not fail to open the roster a second time, even though the
    # tables have already been created.
    roster2 = Roster(os.path.join(tmpdir, 'roster.db'))
    roster2.close()


def test_makes_directories(tmpdir):
    roster = Roster(os.path.join(tmpdir, 'foo', 'bar'))
    roster.close()


def test_set_user_attendance(roster):
    bob = User('1', 'Bob', 'avatar1')
    jay = User('2', 'Jay', 'avatar2')
    cara = User('3', 'Cara', 'avatar3')

    roster.set_user_attendance(bob, True)
    roster.set_user_attendance(jay, True)
    roster.set_user_attendance(cara, False)
    assert list(roster.attending_users()) == [bob, jay]

    roster.set_user_attendance(jay, False)
    roster.set_user_attendance(cara, True)
    assert list(roster.attending_users()) == [bob, cara]


def test_set_user_attendance_updates_user(roster):
    steve = User('1', 'Steve', 'avatar1')
    roster.set_user_attendance(steve, True)

    steve2 = steve._replace(avatar='avatar2')
    roster.set_user_attendance(steve2, True)

    assert list(roster.attending_users()) == [steve2]


def test_attending_users_sorted_by_nick(roster):
    steve = User('1', 'Steve', 'avatar1')
    jay = User('2', 'Jay', 'avatar2')
    bob = User('3', 'Bob', 'avatar3')
    evan = User('4', 'Evan', 'avatar4')
    cara = User('5', 'Cara', 'avatar5')
    for user in [steve, jay, bob, evan, cara]:
        roster.set_user_attendance(user, True)

    assert list(roster.attending_users()) == [bob, cara, evan, jay, steve]


def test_update_users_preserves_attendance(roster):
    bob = User('1', 'Bob', 'avatar1')
    roster.set_user_attendance(bob, True)

    bob2 = bob._replace(avatar='avatar2')
    roster.update_users([bob2])
    assert list(roster.attending_users()) == [bob2]

    roster.set_user_attendance(bob, False)
    bob3 = bob2._replace(nick='Robert')
    roster.update_users([bob3])
    assert list(roster.attending_users()) == []


def test_update_users_does_not_remove_users(roster):
    evan = User('1', 'Evan', 'avatar1')
    steve = User('2', 'Steve', 'avatar2')
    roster.set_user_attendance(evan, True)
    roster.set_user_attendance(steve, True)

    roster.update_users([evan])
    assert list(roster.attending_users()) == [evan, steve]


def test_update_users_accepts_unknown_users(roster):
    user1 = User('1', 'Bob', 'avatar1')
    roster.update_users([user1])