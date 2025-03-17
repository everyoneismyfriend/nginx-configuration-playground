from pathlib import Path

import pytest
import requests

base_path = Path(__file__).parent


def test_intercept_404(nginx_container):
    nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'c01_intercept_404' / 'origin.conf',
        name='origin',
    )
    nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'c01_intercept_404' / 'backend.conf',
        name='backend',
    )
    cache_container = nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'c01_intercept_404' / 'cache.conf',
        name='cache',
    )

    response = requests.get(cache_container.url + '/origin/existing-resource')
    assert response.status_code == 200
    assert 'origin' in response.text

    response = requests.get(cache_container.url + '/origin/nonexistent-resource')
    assert response.status_code == 200
    assert 'backend' in response.text


def test_single_source(nginx_image, nginx_container):
    file_name = 'SampleVideo_1280x720_10mb.mp4'
    nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'c02_semi_adaptive_vod' / 'origin.conf',
        volumes={base_path / 'origin': '/media'},
        name='origin',
    )
    vod_image = nginx_image(
        tag='test-image:latest',
        dockerfile=base_path / 'c02_semi_adaptive_vod' / 'Dockerfile',
    )
    vod_container = nginx_container(
        image_tag=vod_image.tag,
        config=base_path / 'c02_semi_adaptive_vod' / 'vod.conf',
        name='vod',
    )

    response = requests.get(vod_container.url + f'/hls/{file_name}/master.m3u8')
    assert response.status_code == 200
    assert '#EXTM3U' in response.text


@pytest.mark.current
def test_multiple_sources(nginx_image, nginx_container):
    file_names = [
        'SampleVideo_1280x720_10mb__240p.mp4',
        'SampleVideo_1280x720_10mb__360p.mp4',
        'SampleVideo_1280x720_10mb__480p.mp4',
        'SampleVideo_1280x720_10mb__720p.mp4',
    ]
    combined_file_name = 'SampleVideo_1280x720_10mb__,240,360,480,720,p.mp4.urlset'
    nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'c02_semi_adaptive_vod' / 'origin.conf',
        volumes={base_path / 'origin': '/media'},
        name='origin',
    )
    vod_image = nginx_image(
        tag='test-image:latest',
        dockerfile=base_path / 'c02_semi_adaptive_vod' / 'Dockerfile',
    )
    vod_container = nginx_container(
        image_tag=vod_image.tag,
        config=base_path / 'c02_semi_adaptive_vod' / 'vod.conf',
        name='vod',
    )

    response = requests.get(vod_container.url + f'/hls/{combined_file_name}/master.m3u8')
    assert response.status_code == 200
    assert '#EXTM3U' in response.text
    assert all(file_name in response.text for file_name in file_names)
