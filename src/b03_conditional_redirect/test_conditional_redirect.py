from pathlib import Path

import pytest
import requests

from src.utils import NginxContainer, parse_uri

base_path = Path(__file__).parent


@pytest.fixture(scope='module')
def gateway(nginx_container) -> NginxContainer:
    nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'api.conf',
        name='old_api',
    )
    nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'api.conf',
        name='new_api',
    )

    return nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'gateway.conf',
        name='gateway',
    )


@pytest.mark.parametrize(
    ['host', 'from_datetime', 'path', 'exp_path'],
    [
        (
            'new-api.com',
            '2024-10-09 14:00:00+00:00',
            '/api/partner/rest/v1/s3_buckets/42/stats/',
            '/api/partner/rest/v1/s3_buckets/42/stats/',
        ),
        (
            'new-api.com',
            '2024-10-09 10:00:00+00:00',
            '/api/partner/rest/v1/s3_buckets/42/stats/',
            '/api/partner/rest/v1/s3_buckets/42/stats/',
        ),
        (
            'old-api.com',
            '2024-10-09 14:00:00+00:00',
            '/api/v1/buckets/42/',
            '/api/partner/rest/v1/s3_buckets/42/stats/',
        ),
        (
            'old-api.com',
            '2024-10-09 10:00:00+00:00',
            '/api/v1/buckets/42/',
            '/api/v1/buckets/42/',
        ),
    ],
)
def test_conditional_redirect(gateway, host, from_datetime, path, exp_path):
    headers = {'Host': host}
    params = {'from_datetime': from_datetime}

    response = requests.get(gateway.url + path, headers=headers, params=params)

    assert response.status_code == 200
    upstream_uri = response.headers['Upstream-Uri']
    upstream_path, upstream_params = parse_uri(upstream_uri)
    assert upstream_path == exp_path
    assert upstream_params == params
