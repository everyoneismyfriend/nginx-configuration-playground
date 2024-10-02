import urllib.parse

import requests
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for


class NginxContainer(DockerContainer):
    def __init__(self, image: str = 'nginx:latest', port: int = 80, **kwargs) -> None:
        super().__init__(image, **kwargs)

        self.port = port
        self.with_exposed_ports(self.port)

    @property
    def url(self) -> str:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)

        return urllib.parse.urlunsplit(('http', f'{host}:{port}', '', '', ''))

    def start(self) -> 'NginxContainer':
        super().start()

        wait_for(self.is_healthy)

        return self

    def is_healthy(self) -> bool:
        try:
            response = requests.get(self.url, timeout=1)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as ex:
            raise ConnectionError() from ex

        return response.status_code < 500
