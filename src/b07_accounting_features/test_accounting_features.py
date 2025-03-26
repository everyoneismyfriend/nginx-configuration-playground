import json
import re
from pathlib import Path
from typing import Callable

import pytest
import requests
from testcontainers.core.waiting_utils import wait_for_logs

from src.utils import NginxContainer

base_path = Path(__file__).parent


@pytest.fixture(scope='module')
def image(nginx_image):
    return nginx_image(
        tag='test-image:latest',
        dockerfile=base_path / 'Dockerfile',
    )


@pytest.fixture
def config(temp_file) -> Callable[..., Path]:
    config_template = '''
        worker_processes 1;

        events {{
          worker_connections 1024;
        }}

        http {{
          accounting on;
          accounting_interval 1;
          accounting_log /var/log/nginx/access.log notice;

          server {{
            listen 80 default_server;
            server_name _;

            location /test {{
              accounting_id "{accounting_id}";
              return 200;
            }}
          }}
        }}
    '''

    def factory(accounting_id: str) -> Path:
        config = config_template.format(accounting_id=accounting_id)
        temp_file.write_text(config)

        return temp_file

    return factory


def extract_accounting_log(container: NginxContainer) -> dict:
    wait_for_logs(container, 'accounting_id', timeout=2)
    logs = [log.decode() for log in container.get_logs() if log]
    accounting_log_str, *_ = [log for log in logs if 'accounting_id' in log]

    result = re.search(r'.*({\s"accounting".*}).*', accounting_log_str)
    if not result:
        raise ValueError('accounting log not found')

    accounting_log = json.loads(result.group(1))

    return accounting_log['accounting']


def test_accounting_id_without_features(image, nginx_container, config):
    container = nginx_container(
        image_tag=image.tag,
        config=config(accounting_id='example.com'),
    )

    response = requests.get(container.url + '/test')

    assert response.status_code == 200
    accounting_log = extract_accounting_log(container)
    assert 'features' not in accounting_log


def test_accounting_id_with_single_feature(image, nginx_container, config):
    container = nginx_container(
        image_tag=image.tag,
        config=config(accounting_id='example.com[4]'),
    )

    response = requests.get(container.url + '/test')

    assert response.status_code == 200
    accounting_log = extract_accounting_log(container)
    assert 'features' in accounting_log
    assert '4' in accounting_log['features']


def test_accounting_id_with_multiple_features(image, nginx_container, config):
    container = nginx_container(
        image_tag=image.tag,
        config=config(accounting_id='example.com[4,5]'),
    )

    response = requests.get(container.url + '/test')

    assert response.status_code == 200
    accounting_log = extract_accounting_log(container)
    assert 'features' in accounting_log
    assert '4' in accounting_log['features']
    assert '5' in accounting_log['features']
