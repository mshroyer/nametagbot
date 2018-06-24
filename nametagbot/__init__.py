import appdirs
import configparser
import os

from collections import namedtuple

__all__ = ['Config', 'ConfigError', 'User']

User = namedtuple('User', ['user_id', 'nick', 'avatar'])


class Config:
    def __init__(self, path=None):
        if not path:
            path = Config._default_path()

        self.c = configparser.ConfigParser()
        self.c.read(path)

    def server_id(self):
        try:
            return self.c['roster']['ServerId']
        except KeyError:
            raise ConfigError('roster.ServerId not configured')

    def bot_token(self):
        try:
            return self.c['auth']['BotToken']
        except KeyError:
            raise ConfigError('auth.BotToken not configured')

    @staticmethod
    def _default_path():
        return os.path.join(
            appdirs.user_config_dir('nametagbot'), 'config.ini')


class ConfigError(Exception):
    def __init__(self, message):
        super().__init__(message)
