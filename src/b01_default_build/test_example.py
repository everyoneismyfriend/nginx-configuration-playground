from pathlib import Path

import pytest
import requests
from src.utils import NginxContainer

base_path = Path(__file__).parent


@pytest.fixture(scope='module')
def nginx(nginx_image, nginx_container) -> NginxContainer:
    image = nginx_image('test-image:latest', dockerfile=base_path / 'Dockerfile')

    return nginx_container(image.tag, config=base_path / 'c01_example.conf')


def test_example_1(nginx):
    response = requests.get(nginx.url + '/test')

    assert response.status_code == 200


def test_example_2(nginx_container):
    nginx = nginx_container('nginx:latest', config=base_path / 'c01_example.conf')
    response = requests.get(nginx.url + '/test')

    assert response.status_code == 200
