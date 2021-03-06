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
"""Connects to a server.

"""

import argparse
import discord
import logging
from queue import Queue
import sys
from threading import Thread

from .config import Config
from . import chat


def main():
    logging.basicConfig(level=logging.INFO)

    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('-c', '--config', type=str, help='configuration file path')
    args = p.parse_args()

    config = Config(args.config)
    _run_bot(config)


def _run_bot(config):
    roster_messages = Queue()
    roster_thread = Thread(
        target=_roster_actor, args=(config, roster_messages))
    roster_thread.start()

    client = discord.Client()

    @client.event
    async def on_ready():
        logging.info('Connected to server %s', config.server_id)

        bot_member = client.get_server(config.server_id).me
        logging.info('Roles: %s',
                     list(map(lambda role: role.name, bot_member.roles)))
        perms = bot_member.server_permissions
        logging.info('Permission to read messages: %s', perms.read_messages)

    @client.event
    async def on_message(message):
        action = chat.parse_message(message, config.server_id, client.user)
        if action is None:
            return

        logging.info('Action: %s', action)
        roster_messages.put(action)

    client.run(config.bot_token)

    roster_messages.put(('QUIT', ))
    roster_thread.join()


def _roster_actor(config, messages):
    """Act on messages for the roster.

    The Roster class is not thread-safe, so we use a single actor thread to
    serialize messages for the database.  Messages can be:

    ('QUIT')
    ('ATTENDING', User(...))

    """
    logging.info('Roster actor is starting')

    try:
        with config.get_roster() as roster:
            while True:
                message = messages.get()

                if message[0] == 'QUIT':
                    logging.info('Roster actor is quitting')
                    return

                if message[0] == 'ATTENDING':
                    user = message[1]
                    logging.info('Setting attendance to True: %s', user)
                    roster.set_user_attendance(user, True)
    except Exception as e:
        logging.critical('Roster actor failed: %s', e)
        sys._exit(1)
