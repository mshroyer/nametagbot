import os.path
import responses

from nametagbot import User
from nametagbot.data import AvatarCache, AVATAR_CDN_PREFIX


@responses.activate
def test_get_avatar(tmpdir):
    responses.add(
        responses.GET,
        AVATAR_CDN_PREFIX + '123/avatar1.png',
        status=200,
        content_type='image/png',
        body=b'imagedata')

    cache = AvatarCache(os.path.join(tmpdir, 'cache'))
    output_path = os.path.join(tmpdir, 'out.png')
    cache.get_avatar(User('123', 'foo', 'avatar1'), output_path)

    with open(output_path, 'rb') as f:
        data = f.read()

    assert data == b'imagedata'
