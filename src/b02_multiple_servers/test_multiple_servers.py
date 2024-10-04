from pathlib import Path

import requests

base_path = Path(__file__).parent


def test_prebuilt_image(nginx_container):
    for num in (1, 2, 3):
        nginx_container(
            image_tag='nginx:latest',
            config=base_path / 'edge.conf',
            name=f'edge_{num}',
        )
    balancer = nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'balancer.conf',
        name='balancer',
    )

    response = requests.get(balancer.url + '/test')

    assert response.status_code == 200
