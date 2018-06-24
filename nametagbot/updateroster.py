"""Update nametagbot's roster from Discord.

This command updates nametagbot's roster from the server(s). Updated nicks
and avatar IDs are retrieved for all users. Records of user attendance are
not altered by this command.

One or more servers may optionally be specified, in which case users will
only be updated from those servers. By default, the command will update
users from all servers the bot has joined.

"""

import argparse
import discord
import logging

from . import Config, User
from .data import Roster


def main():
    logging.basicConfig(level=logging.INFO)

    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('-c', '--config', type=str, help='configuration file path')
    args = p.parse_args()

    _update_roster(
        Config(args.config), Roster('/Users/mshroyer/Desktop/nametagbot.db'),
        discord.Client())


def _update_roster(config, roster, client):
    @client.event
    async def on_ready():
        logging.info('Ready!')

        users = []
        for member in client.get_server(config.server_id()).members:
            nick = member.nick
            if nick is None:
                nick = member.name

            users.append(User(member.id, nick, member.avatar))

        logging.info('Updating roster with %d users', len(users))
        roster.update_users(users)

        logging.info('Logging out')
        await client.logout()

    client.run(config.bot_token())
