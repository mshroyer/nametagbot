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

from nametagbot import User

__all__ = ['parse_content']

_ATTENDING_PATTERN = re.compile(
    '|'.join(
        map(lambda p: p.format(user=r'([^\s]+)',
                               nametag=r'(?:a (?:name)?tag|one)'), [
            '{user} is attending',
            '{user} will be attending',
            '{user} will be there',
            '{user} is going',
            '{user} wants? {nametag}',
            '{user} would like {nametag}',
            'make {user} {nametag}',
            'make {nametag} for {user}',
        ])), re.I)

_TARGET_ID_PATTERN = re.compile('<@([^\s]+)>')


def parse_content(message_content):
    match = _ATTENDING_PATTERN.search(message_content)
    if match is None:
        return None

    return ('ATTENDING',
            next(group for group in match.groups() if group is not None))


def parse_message(message, server_id, bot_discord_user):
    if message.server is not None and message.server.id != server_id:
        return None

    if not _mentions_discord_user(message, bot_discord_user):
        return None

    action = parse_content(message.content)
    if action[0] != 'ATTENDING':
        return None

    discord_user = _target_discord_user(message, action[1])
    if discord_user is None:
        return None

    return (action[0], _nametagbot_user(discord_user))


def _target_discord_user(message, target_name):
    if target_name.lower() in ('i', 'me'):
        return message.author

    match = _TARGET_ID_PATTERN.match(target_name)
    if match is None:
        return None

    target_id = match.group(1)
    for mention in message.mentions:
        if mention.id == target_id:
            return mention


def _mentions_discord_user(message, discord_user):
    for mention in message.mentions:
        if mention == discord_user:
            return True
    return False


def _nametagbot_user(discord_user):
    nick = discord_user.name
    if discord_user.nick is not None:
        nick = discord_user.nick

    return User(discord_user.id, nick, discord_user.discriminator,
                discord_user.avatar)
