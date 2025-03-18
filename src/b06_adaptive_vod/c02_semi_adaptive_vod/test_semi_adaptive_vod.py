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
        name='origin-2',
    )
    vod_image = nginx_image(
        tag='test-image:latest',
        dockerfile=base_path / 'Dockerfile',
    )

    return nginx_container(
        image_tag=vod_image.tag,
        config=base_path / 'vod.conf',
        name='vod-2',
    )


def test_single_source(vod_container):
    file_name = 'SampleVideo_1280x720_10mb.mp4'

    response = requests.get(vod_container.url + f'/hls/{file_name}/master.m3u8')

    assert response.status_code == 200
    assert '#EXTM3U' in response.text


def test_multiple_sources(vod_container):
    file_names = [
        'SampleVideo_1280x720_10mb__240p.mp4',
        'SampleVideo_1280x720_10mb__360p.mp4',
        'SampleVideo_1280x720_10mb__480p.mp4',
        'SampleVideo_1280x720_10mb__720p.mp4',
    ]
    combined_file_name = 'SampleVideo_1280x720_10mb__,240,360,480,720,p.mp4.urlset'

    response = requests.get(vod_container.url + f'/hls/{combined_file_name}/master.m3u8')

    assert response.status_code == 200
    assert '#EXTM3U' in response.text
    assert all(file_name in response.text for file_name in file_names)
