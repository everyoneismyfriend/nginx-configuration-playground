from pathlib import Path

import requests

base_path = Path(__file__).parent


def test_intercept_404(nginx_image, nginx_container):
    nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'c01_intercept_404' / 'origin.conf',
        name='origin',
    )
    nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'c01_intercept_404' / 'backend.conf',
        name='backend',
    )
    cache_container = nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'c01_intercept_404' / 'cache.conf',
        name='cache',
    )

    response = requests.get(cache_container.url + '/origin/existing-resource')
    assert response.status_code == 200
    assert 'origin' in response.text

    response = requests.get(cache_container.url + '/origin/nonexistent-resource')
    assert response.status_code == 200
    assert 'backend' in response.text
