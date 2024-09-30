import os.path

import pytest
import requests
from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage


@pytest.fixture(scope='session')
def nginx_image() -> DockerImage:
    image = DockerImage(
        path='./',
        dockerfile_path='./Dockerfile',
        tag='test-image:latest',
        clean_up=False,
    )
    image.build()
    yield image
    image.remove()


@pytest.fixture(scope='module')
def nginx_container(nginx_image: DockerImage) -> DockerContainer:
    container = DockerContainer(image='test-image:latest') \
        .with_exposed_ports(80) \
        .with_volume_mapping(
            host=os.path.abspath('./c01_example.conf'),
            container='/etc/nginx/nginx.conf',
        )
    container.start()
    yield container
    container.stop()


class Nginx:
    def __init__(self, container: DockerContainer) -> None:
        self._container = container

    @property
    def base_url(self) -> str:
        host = self._container.get_container_host_ip()
        port = self._container.get_exposed_port(80)

        return f'http://{host}:{port}'

    # ToDo: add nginx management methods


@pytest.fixture
def nginx(nginx_container: DockerContainer) -> Nginx:
    return Nginx(nginx_container)


def test_example1(nginx: Nginx):
    response = requests.get(nginx.base_url + '/test')

    assert response.status_code == 200
