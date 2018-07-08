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
import re

__all__ = ['parse_content']

_ATTENDING_PATTERN = re.compile(
    '|'.join(
        map(lambda p: p.format(user=r'([^\s]+)', nametag=r'(?:name)?tag'), [
            '{user} is attending',
            '{user} will be attending',
            '{user} will be there',
            '{user} is going',
            '{user} wants? a {nametag}',
            '{user} wants? one',
            'make {user} a {nametag}',
            'make a {nametag} for {user}',
        ])), re.I)


def parse_content(message_content):
    match = _ATTENDING_PATTERN.search(message_content)
    if match is None:
        return None

    return ('ATTENDING',
            next(group for group in match.groups() if group is not None))
