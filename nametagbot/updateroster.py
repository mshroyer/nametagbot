import discord
import logging

from nametagbot import Config, User
from nametagbot.db import Database

SERVER_ID = '459560440113135618'


def main():
    logging.basicConfig(level=logging.INFO)

    config = Config()
    client = discord.Client()
    db = Database('/Users/mshroyer/Desktop/nametagbot.db')

    @client.event
    async def on_ready():
        print('Ready!')
        print('Connected to servers: {}'.format(
            [server.id for server in client.servers]))
        print('Can see members: {}'.format(
            [str(member) for member in client.get_all_members()]))

        users = []
        for member in client.get_server(SERVER_ID).members:
            nick = member.nick
            if nick is None:
                nick = member.name

            users.append(User(member.id, nick, member.avatar))

        db.update_roster(users)
        await client.logout()

    client.run(config.bot_token())
