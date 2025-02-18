import os
from pathlib import Path

import dotenv
import requests
from testcontainers.core.waiting_utils import wait_for_logs

base_path = Path(__file__).parent
dotenv.load_dotenv()


def test_custom_image(nginx_image, nginx_container):
    token = os.getenv('NGX_TRAFFIC_ACCOUNTING_GITLAB_TOKEN')
    assert token, 'accounting repo token is not set'
    branch = os.getenv('NGX_TRAFFIC_ACCOUNTING_GIT_BRANCH', 'main')
    image = nginx_image(
        tag='test-image:latest',
        dockerfile=base_path / 'Dockerfile',
        build_args={
            'NGX_TRAFFIC_ACCOUNTING_GITLAB_TOKEN': token,
            'NGX_TRAFFIC_ACCOUNTING_GIT_BRANCH': branch,
        },
    )
    container = nginx_container(image_tag=image.tag, config=base_path / 'nginx.conf')

    accounted_response = requests.get(container.url + '/test')
    ignored_response = requests.get(container.url + '/default')
    wait_for_logs(container, 'accounting_id', timeout=2)
    logs = [log.decode() for log in container.get_logs() if log]

    assert accounted_response.status_code == 200
    assert ignored_response.status_code == 200
    assert len(logs) == 1
    assert 'test' in logs[0]
    assert 'default' not in logs[0]
