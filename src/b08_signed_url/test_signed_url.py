import binascii
import hashlib
import hmac
import time
from pathlib import Path

import pytest
import requests

from src.utils import NginxContainer

base_path = Path(__file__).parent


def generate_token(*, signature_key: str, lifetime: int, acl_path: str) -> str:
    exp = int(time.time() + lifetime)
    token_params = f'exp={exp}~acl={acl_path}'

    token_hmac = hmac.new(
        key=binascii.a2b_hex(signature_key.encode()),
        msg=token_params.encode(),
        digestmod=hashlib.sha256,
    )
    token_digest = token_hmac.hexdigest()

    return f'{token_params}~hmac={token_digest}'


@pytest.fixture(scope="module")
def origin(nginx_container) -> NginxContainer:
    return nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'origin.conf',
        volumes={base_path / 'root': '/root'},
        name='origin',
    )


@pytest.fixture(scope="module")
def cache(nginx_image, nginx_container, origin) -> NginxContainer:
    image = nginx_image(
        tag='test-image:latest',
        dockerfile=base_path / 'Dockerfile',
    )

    return nginx_container(
        image_tag=image.tag,
        config=base_path / 'cache.conf',
        name='cache',
    )


def test_request_without_token(cache):
    response = requests.get(cache.url + '/test')

    assert response.status_code == 403


@pytest.mark.parametrize(
    ['signature_key', 'lifetime', 'acl_path', 'url_path', 'exp_code'],
    [
        ('d00d', 60, '/*', '/example.jpg', 200),
        ('badd', 60, '/*', '/example.jpg', 403),
        ('d00d', -60, '/*', '/example.jpg', 403),
        ('d00d', 60, '/private/*', '/private/example.jpg', 200),
        ('d00d', 60, '/private/*', '/example.jpg', 403),
        ('d00d', 60, '/example.jpg', '/example.jpg', 200),
        ('d00d', 60, '/example.jpg', '/example.jpg.bak', 403),
        ('d00d', 60, '/private/example.jpg', '/private/example.jpg', 200),
    ],
)
def test_request_with_token(cache,
                            signature_key,
                            lifetime,
                            acl_path,
                            url_path,
                            exp_code):
    token = generate_token(
        signature_key=signature_key,
        lifetime=lifetime,
        acl_path=acl_path,
    )

    response = requests.get(cache.url + f'{url_path}?token={token}')

    assert response.status_code == exp_code
