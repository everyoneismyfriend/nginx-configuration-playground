from pathlib import Path

import pytest
import requests

base_path = Path(__file__).parent


@pytest.fixture(scope='module')
def backend_container(nginx_container):
    return nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'backend.conf',
        name='backend-4',
    )


@pytest.fixture(scope='module')
def vod_container(nginx_image, nginx_container, backend_container):
    nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'origin.conf',
        volumes={base_path.parent / 'media': '/media'},
        name='origin-4',
    )
    nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'storage.conf',
        volumes={base_path.parent / 'media': '/media'},
        name='storage-4',
    )
    vod_image = nginx_image(
        tag='test-image:latest',
        dockerfile=base_path / 'Dockerfile',
    )

    return nginx_container(
        image_tag=vod_image.tag,
        config=base_path / 'vod.conf',
        name='vod-4',
    )


def test_non_adaptive_resource(vod_container):
    file_name = 'SampleVideo_1280x720_10mb.mp4'
    path = f'/hls/non-adaptive/{file_name}/master.m3u8'

    response = requests.get(vod_container.url + path)

    assert response.status_code == 200
    assert '#EXTM3U' in response.text


def test_adaptive_resource_existing_resource(vod_container):
    file_names = [
        'SampleVideo_1280x720_10mb__240p.mp4',
        'SampleVideo_1280x720_10mb__360p.mp4',
        'SampleVideo_1280x720_10mb__480p.mp4',
        'SampleVideo_1280x720_10mb__720p.mp4',
    ]
    file_name = 'SampleVideo_1280x720_10mb.mp4'
    path = f'/hls/adaptive/{file_name}/master.m3u8'

    response = requests.get(vod_container.url + path)

    assert response.status_code == 200
    assert '#EXTM3U' in response.text
    assert all(file_name in response.text for file_name in file_names)


def test_adaptive_resource_nonexistent_resource(vod_container, backend_container):
    file_name = 'non-rescaled.mp4'
    path = f'/hls/adaptive/{file_name}/master.m3u8'

    response = requests.get(
        vod_container.url + path,
        headers={'vod-url': vod_container.url},
    )

    assert response.status_code == 200
    assert '#EXTM3U' in response.text
    backend_logs = '\n'.join(log.decode() for log in backend_container.get_logs())
    assert file_name in backend_logs
