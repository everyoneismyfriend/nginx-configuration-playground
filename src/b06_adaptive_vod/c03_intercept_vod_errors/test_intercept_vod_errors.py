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
        name='origin-3',
    )
    nginx_container(
        image_tag='nginx:latest',
        config=base_path / 'backend.conf',
        name='backend-3',
    )
    vod_image = nginx_image(
        tag='test-image:latest',
        dockerfile=base_path / 'Dockerfile',
    )

    return nginx_container(
        image_tag=vod_image.tag,
        config=base_path / 'vod.conf',
        name='vod-3',
    )


@pytest.mark.parametrize(
    'file_name',
    [
        # Исходя из того, что рескейлинг происходит на нашей стороне, и доступ на запись
        # есть только у нас, единственная возможная ошибка - отсутствие файла в одном из
        # разрешений
        'SampleVideo_1280x720_10mb__,240,360,480,720,1080,p.mp4.urlset',  # Missing file
        'SampleVideo_1280x720_10mb__,144,240,360,480,720,p.mp4.urlset',   # Invalid file
    ],
)
def test_intercept_vod_errors(vod_container, file_name):
    response = requests.get(vod_container.url + f'/hls/{file_name}/master.m3u8')

    assert response.status_code == 200
    assert 'backend' in response.text
