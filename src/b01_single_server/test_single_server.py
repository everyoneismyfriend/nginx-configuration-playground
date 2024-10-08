from pathlib import Path

import requests

base_path = Path(__file__).parent


def test_custom_image(nginx_image, nginx_container):
    image = nginx_image(
        tag='test-image:latest',
        dockerfile=base_path / 'Dockerfile',
    )
    container = nginx_container(
        image_tag=image.tag,
        config=base_path / 'nginx.conf',
    )

    response = requests.get(container.url + '/test')

    assert response.status_code == 200


def test_prebuilt_image(nginx_container):
    container = nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'nginx.conf',
    )

    response = requests.get(container.url + '/test')

    assert response.status_code == 200
