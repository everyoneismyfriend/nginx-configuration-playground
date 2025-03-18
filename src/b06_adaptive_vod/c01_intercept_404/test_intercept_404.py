from pathlib import Path

import requests

base_path = Path(__file__).parent


def test_intercept_404(nginx_container):
    nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'origin.conf',
        name='origin-1',
    )
    nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'backend.conf',
        name='backend-1',
    )
    cache_container = nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'cache.conf',
        name='cache-1',
    )

    response = requests.get(cache_container.url + '/origin/existing-resource')

    assert response.status_code == 200
    assert 'origin' in response.text

    response = requests.get(cache_container.url + '/origin/nonexistent-resource')

    assert response.status_code == 200
    assert 'backend' in response.text
