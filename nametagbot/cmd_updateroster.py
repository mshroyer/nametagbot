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

from . import User
from .config import Config


def main():
    logging.basicConfig(level=logging.INFO)

    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('-c', '--config', type=str, help='configuration file path')
    args = p.parse_args()

    config = Config(args.config)
    _update_roster(config, config.get_roster())


def _update_roster(config, roster):
    client = discord.Client()
    users = []
    errors = []

    def retrieve_users():
        nonlocal users

        logging.info('Retrieving users from server %s', config.server_id)
        for member in client.get_server(config.server_id).members:
            nick = member.nick if member.nick is not None else member.name
            users.append(User(member.id, nick, member.avatar))

    @client.event
    async def on_ready():
        nonlocal errors

        logging.info('Ready!')
        try:
            retrieve_users()
        except Exception as e:
            logging.error('Error retrieving users: %s', e)

            # discord.py's event system would otherwise eat an exception,
            # so we need to manually propagate it outside the event loop in
            # order to stop the script.
            errors.append(e)
        finally:
            logging.info('Logging out')
            await client.logout()

    client.run(config.bot_token)

    for e in errors:
        raise Exception('Error in event loop') from e

    logging.info('Updating roster with %d users', len(users))
    roster.update_users(users)

    logging.info('Done!')
