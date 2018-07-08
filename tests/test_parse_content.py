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
from nametagbot.chat import parse_content


def test_no_action():
    assert parse_content("Let's get some poutine") is None


def test_add_self():
    assert parse_content('I want a nametag') == ('ATTENDING', 'I')
    assert parse_content('Make me a nametag') == ('ATTENDING', 'me')
    assert parse_content('<@123> I want a nametag') == ('ATTENDING', 'I')
    assert parse_content('<@123> make a nametag for me') == ('ATTENDING', 'me')


def test_add_other_user():
    assert parse_content('<@123> <@456> wants a nametag') == ('ATTENDING',
                                                              '<@456>')
    assert parse_content('<@123> make a nametag for <@456>') == ('ATTENDING',
                                                                 '<@456>')
