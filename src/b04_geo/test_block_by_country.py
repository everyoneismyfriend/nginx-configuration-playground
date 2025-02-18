from pathlib import Path

import requests

base_path = Path(__file__).parent


def test_requests_from_ru_and_by_are_blocked(nginx_image, nginx_container):
    image = nginx_image(tag='test-image:latest', dockerfile=base_path / 'Dockerfile')
    container = nginx_container(image_tag=image.tag, config=base_path / 'nginx.conf')

    addresses = {
        '100.128.0.1': 200,    # US
        '109.105.64.1': 403,   # RU
        '101.60.0.1': 200,     # UK
        '109.123.192.1': 200,  # CZ
        '134.17.0.1': 403,     # BY
        '104.129.96.1': 200,   # CA
    }
    for address, exp_status in addresses.items():
        response = requests.get(
            container.url + '/test',
            headers={'X-Forwarded-For': address},
        )
        assert response.status_code == exp_status
