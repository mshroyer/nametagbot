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
import os.path
import pytest
import responses

from nametagbot import User
from nametagbot.data import AvatarCache, AVATAR_CDN_PREFIX


@pytest.fixture
def cache(tmpdir):
    return AvatarCache(os.path.join(tmpdir, 'cache'))


@responses.activate
def test_get_avatar(cache, tmpdir):
    responses.add(
        responses.GET,
        AVATAR_CDN_PREFIX + '123/avatar1.png',
        status=200,
        content_type='image/png',
        body=b'imagedata')

    user = User('123', 'foo', '1', 'avatar1')
    output_path = os.path.join(tmpdir, 'out.png')
    cache.get_avatar(user, output_path)

    with open(output_path, 'rb') as f:
        data = f.read()

    assert data == b'imagedata'


@responses.activate
def test_does_not_request_cached_avatars(cache, tmpdir):
    responses.add(
        responses.GET,
        AVATAR_CDN_PREFIX + '123/avatar1.png',
        status=200,
        content_type='image/png')

    user = User('123', 'foo', '1', 'avatar1')
    for i in range(3):
        cache.get_avatar(user, os.path.join(tmpdir, 'out{}.png'.format(i)))

    assert len(responses.calls) == 1


@responses.activate
def test_fetches_default_for_user_without_avatar(cache, tmpdir):
    responses.add(
        responses.GET,
        AVATAR_CDN_PREFIX + 'embed/avatars/1.png',
        status=200,
        content_type='image/png',
        body=b'default_avatar_1')

    user = User('123', 'foo', '1', '')
    output_path = os.path.join(tmpdir, 'out.png')
    cache.get_avatar(user, output_path)

    with open(output_path, 'rb') as f:
        data = f.read()

    assert data == b'default_avatar_1'


@responses.activate
def test_not_found_avatar_raises_exception(cache, tmpdir):
    responses.add(
        responses.GET, AVATAR_CDN_PREFIX + '123/avatar1.png', status=404)

    user = User('123', 'foo', '1', 'avatar1')
    output_path = os.path.join(tmpdir, 'out.png')
    with pytest.raises(ValueError):
        cache.get_avatar(user, output_path)


@responses.activate
def test_unexpected_content_type_raises_exception(cache, tmpdir):
    responses.add(
        responses.GET,
        AVATAR_CDN_PREFIX + '123/avatar1.png',
        status=200,
        content_type='image/jpeg')

    user = User('123', 'foo', '1', 'avatar1')
    output_path = os.path.join(tmpdir, 'out.png')
    with pytest.raises(ValueError):
        cache.get_avatar(user, output_path)
