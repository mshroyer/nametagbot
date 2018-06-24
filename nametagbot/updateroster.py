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

from nametagbot import Config, Roster, User

SERVER_ID = '459560440113135618'


def main():
    logging.basicConfig(level=logging.INFO)

    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument(
        '-s',
        '--server',
        action='append',
        type=str,
        help='specific server id(s) from which to update')
    args = p.parse_args()

    config = Config()
    roster = Roster('/Users/mshroyer/Desktop/nametagbot.db')
    server_ids = args.server
    client = discord.Client()

    @client.event
    async def on_ready():
        logging.info('Ready!')

        nonlocal server_ids
        if not server_ids:
            server_ids = [server.id for server in client.servers]

        logging.info('Updating roster from server IDs: %r', server_ids)

        users = []
        for server_id in server_ids:
            for member in client.get_server(server_id).members:
                nick = member.nick
                if nick is None:
                    nick = member.name

            users.append(User(member.id, nick, member.avatar))

        roster.update_users(users)
        await client.logout()

    client.run(config.bot_token())
