import discord
import logging

from nametagbot import Config, User
from nametagbot.db import Database


def main():
    logging.basicConfig(level=logging.INFO)

    config = Config()
    client = discord.Client()
    db = Database('/Users/mshroyer/Desktop/nametagbot.db')

    @client.event
    async def on_ready():
        print('Ready!')
        print('Connected to servers: {}'.format(
            [str(server) for server in client.servers]))
        print('Can see members: {}'.format(
            [str(member) for member in client.get_all_members()]))

        db.update_roster([
            User(member.id, member.nick, member.avatar)
            for member in client.get_server(81384788765712384).members
        ])

        await client.logout()

    client.run(config.bot_token())
