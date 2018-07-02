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
import appdirs
import configparser
import os
import os.path

from .data import AvatarCache, Roster

APPNAME = 'nametagbot'


class Config:
    """nametagbot application configuration.

    This class represents a nametagbot configuration, which is based on an
    .ini configuration file.  It also includes factory methods to
    instantiate dependencies based on the app's config, and in that sense
    serves as an IoC container.

    """

    def __init__(self, path=None):
        if not path:
            path = Config._default_config_path()

        self.c = configparser.ConfigParser()
        self.c.add_section('files')
        self.c.read(path)

    @property
    def server_id(self):
        return self._get_required('connection', 'ServerId')

    @property
    def bot_token(self):
        return self._get_required('connection', 'BotToken')

    @property
    def data_path(self):
        return self.c['files'].get('DataDir', appdirs.user_config_dir(APPNAME))

    @property
    def cache_path(self):
        return self.c['files'].get('CacheDir', appdirs.user_cache_dir(APPNAME))

    def get_roster(self):
        return Roster(os.path.join(self.data_path, 'roster.db'))

    def get_avatar_cache(self):
        return AvatarCache(os.path.join(self.cache_path, 'avatars'))

    @staticmethod
    def _default_config_path():
        return os.path.join(appdirs.user_config_dir(APPNAME), 'config.ini')

    def _get_required(self, section, option):
        try:
            return self.c[section][option]
        except KeyError as e:
            raise ConfigError('{}.{} not configured'.format(section,
                                                            option)) from e


class ConfigError(Exception):
    def __init__(self, message):
        super().__init__(message)
