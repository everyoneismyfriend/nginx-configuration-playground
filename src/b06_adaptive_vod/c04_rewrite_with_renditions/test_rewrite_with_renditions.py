from pathlib import Path

import pytest
import requests

base_path = Path(__file__).parent


@pytest.fixture(scope='module')
def vod_container(nginx_image, nginx_container):
    nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'origin.conf',
        volumes={base_path.parent / 'media': '/media'},
        name='origin-4',
    )
    nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'backend.conf',
        name='backend-4',
    )
    nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'storage_origin.conf',
        volumes={base_path.parent / 'media': '/media'},
        name='storage-origin-4',
    )
    nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'storage.conf',
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


@pytest.mark.current
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
    # print()
    # print(response.status_code)
    # print(response.text)
    #
    # import time
    # for i in range(120, 0, -1):
    #     print(i)
    #     time.sleep(1)

    assert response.status_code == 200
    assert '#EXTM3U' in response.text
    assert all(file_name in response.text for file_name in file_names)


def test_adaptive_resource_nonexistent_resource(vod_container):
    file_name = 'nonexistent.mp4'
    path = f'/hls/adaptive/{file_name}/master.m3u8'

    response = requests.get(vod_container.url + path)

    assert response.status_code == 200
    assert 'backend' in response.text


'''
http://localhost/hls/non-adaptive/SampleVideo_1280x720_10mb.mp4/master.m3u8
http://localhost/hls/adaptive/SampleVideo_1280x720_10mb.mp4/master.m3u8
'''
