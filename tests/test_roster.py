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
import os
import pytest

from nametagbot import User
from nametagbot.data import Roster


@pytest.fixture
def roster(tmpdir):
    r = Roster(os.path.join(str(tmpdir), 'roster.db'))
    yield r
    r.close()


def test_reopen(roster, tmpdir):
    roster.close()

    # We should not fail to open the roster a second time, even though the
    # tables have already been created.
    roster2 = Roster(os.path.join(str(tmpdir), 'roster.db'))
    roster2.close()


def test_makes_directories(tmpdir):
    roster = Roster(os.path.join(str(tmpdir), 'foo', 'bar'))
    roster.close()


def test_set_user_attendance(roster):
    bob = User('1', 'Bob', '1', 'avatar1')
    jay = User('2', 'Jay', '1', 'avatar2')
    cara = User('3', 'Cara', '1', 'avatar3')

    roster.set_user_attendance(bob, True)
    roster.set_user_attendance(jay, True)
    roster.set_user_attendance(cara, False)
    assert list(roster.attending_users()) == [bob, jay]

    roster.set_user_attendance(jay, False)
    roster.set_user_attendance(cara, True)
    assert list(roster.attending_users()) == [bob, cara]


def test_set_user_attendance_updates_user(roster):
    steve = User('1', 'Steve', '1', 'avatar1')
    roster.set_user_attendance(steve, True)

    steve2 = steve._replace(avatar='avatar2')
    roster.set_user_attendance(steve2, True)

    assert list(roster.attending_users()) == [steve2]


def test_attending_users_sorted_by_nick(roster):
    steve = User('1', 'Steve', '1', 'avatar1')
    jay = User('2', 'Jay', '1', 'avatar2')
    bob = User('3', 'Bob', '1', 'avatar3')
    evan = User('4', 'Evan', '1', 'avatar4')
    cara = User('5', 'Cara', '1', 'avatar5')
    for user in [steve, jay, bob, evan, cara]:
        roster.set_user_attendance(user, True)

    assert list(roster.attending_users()) == [bob, cara, evan, jay, steve]


def test_update_users_preserves_attendance(roster):
    bob = User('1', 'Bob', '1', 'avatar1')
    roster.set_user_attendance(bob, True)

    bob2 = bob._replace(avatar='avatar2')
    roster.update_users([bob2])
    assert list(roster.attending_users()) == [bob2]

    roster.set_user_attendance(bob, False)
    bob3 = bob2._replace(nick='Robert')
    roster.update_users([bob3])
    assert list(roster.attending_users()) == []


def test_update_users_does_not_remove_users(roster):
    evan = User('1', 'Evan', '1', 'avatar1')
    steve = User('2', 'Steve', '1', 'avatar2')
    roster.set_user_attendance(evan, True)
    roster.set_user_attendance(steve, True)

    roster.update_users([evan])
    assert list(roster.attending_users()) == [evan, steve]


def test_update_users_accepts_unknown_users(roster):
    user1 = User('1', 'Bob', '1', 'avatar1')
    roster.update_users([user1])
