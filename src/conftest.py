import tempfile
from pathlib import Path
from typing import Callable, Iterator

import pytest
from testcontainers.core.image import DockerImage
from testcontainers.core.network import Network

from src.utils import NginxContainer


def normalize_path(path: Path) -> str:
    return path.absolute().as_posix()


@pytest.fixture
def temp_file() -> Iterator[Path]:
    temp_dir = tempfile.TemporaryDirectory()
    temp_file = Path(temp_dir.name) / 'nginx.conf'
    temp_file.touch()

    yield temp_file

    temp_dir.cleanup()


@pytest.fixture(scope='session')
def nginx_image() -> Iterator[Callable[..., DockerImage]]:
    built_images = {}

    def factory(tag: str,
                dockerfile: Path | None = None,
                build_args: dict | None = None,
                ) -> DockerImage:
        image = built_images.get(tag)

        if not image:
            image = DockerImage(
                tag=tag,
                path=normalize_path(dockerfile.parent),
                dockerfile_path=normalize_path(dockerfile),
                clean_up=False,
            )

            image.build(buildargs=build_args or {})
            built_images[image.tag] = image

        return image

    yield factory

    for built_image in built_images.values():
        built_image.remove()


@pytest.fixture(scope='session')
def network() -> Iterator[Network]:
    network = Network()
    network.create()

    yield network

    network.remove()


@pytest.fixture(scope='session')
def nginx_container(network) -> Iterator[Callable[..., NginxContainer]]:
    running_containers = {}

    def factory(image_tag: str,
                config: Path | str,
                name: str | None = None,
                volumes: dict[Path, str] | None = None,
                ) -> NginxContainer:
        # ToDo: parametrize port and container-side path

        container_key = image_tag, name, normalize_path(config)
        container = running_containers.get(container_key)

        if not container:
            container = NginxContainer(image=image_tag)
            container.with_network(network)
            container.with_volume_mapping(
                host=normalize_path(config),
                container='/etc/nginx/nginx.conf',
            )
            if name is not None:
                container.with_name(name)

            if volumes is not None:
                for host_path, container_path in volumes.items():
                    container.with_volume_mapping(
                        host=normalize_path(host_path),
                        container=container_path,
                    )

            # ToDo: handle failures on startup
            container.start()
            running_containers[container_key] = container

        return container

    yield factory

    for running_container in running_containers.values():
        running_container.stop()
