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

    user = User('123', 'foo', 'avatar1')
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

    user = User('123', 'foo', 'avatar1')
    for i in range(3):
        cache.get_avatar(user, os.path.join(tmpdir, 'out{}.png'.format(i)))

    assert len(responses.calls) == 1


@responses.activate
def test_not_found_avatar_raises_exception(cache, tmpdir):
    responses.add(
        responses.GET,
        AVATAR_CDN_PREFIX + '123/avatar1.png',
        status=404)

    user = User('123', 'foo', 'avatar1')
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

    user = User('123', 'foo', 'avatar1')
    output_path = os.path.join(tmpdir, 'out.png')
    with pytest.raises(ValueError):
        cache.get_avatar(user, output_path)
