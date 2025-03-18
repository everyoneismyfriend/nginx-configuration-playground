- Делаю запрос к http://vod-balancer/hls/example.mp4/master.m3u8?adaptive=true
- В конфиге есть переменная, обозначающая, включена ли функция адаптивного VoD - `adaprive_enabled=true`
- Если не включена, обрабатывает стандартный конфиг
- Если включена, то также есть переменная, в которой содержатся разрешения для адаптивного VoD `renditions_template='...'`
- URL преобразуется к виду http://vod-balancer/hls/example_,48,72,108,0p.mp4.urlset/master.m3u8 при помощи rewrite
- Запрос отправляется к нашему S3, в котором лежат рескейленые данные
- Если запрос завершается с ошибкой 404, перенаправляю на backend (proxy_intercept_errors, https://habr.com/ru/articles/308880/)
  - UPD: `the module returns 502 for any invalid status code returned from upstream`:
    - Если origin возвращает 404, vod отдает 502
    - Если origin отвечает 200, но файл плохой, то vod отвечает 404 (???)
    - Если кривая метадата, vod отвечает тоже 404
- На бэке разбираю опять этот URL, извлекаю оригинальный URL origin и параметры для рескейлинга
- Проверяю наличие рескейленых видео. Создаю задачу (или задачи), запускается рескейлинг
- Клиенту возвращаю страницу с информацией
- При последующих обращениях проверяю наличие запущенной задачи
- Если задача есть, возвращаю прогресс

---

1. Протестировать работу директивы `proxy_intercept_errors`
2. Протестировать формат ответа URL в формате urlset, если какого-то из компонентов нет
3. Собрать минимальную конфигурацию, с которой можно протестировать редиректы
4. Написать и протестировать rewrite правило для генерации multi-source ссылок
  - Запрос к серверу VoD: `http://vod/hls/example.mp4/master.m3u8`
  - Запрос к origin: `http://origin/example__,240,360,480,p.mp4.urlset/master.m3u8`
  - Запрос к backend: `http://backend/?filename=example.mp4&rendition=240&rendition=360&rendition=480`

---

Rescale:

```shell
docker run --rm -it \
    -v $(pwd):/config \
    linuxserver/ffmpeg \
    -i /config/SampleVideo_1280x720_10mb.mp4 \
    -vf scale=426:240 \
    /config/SampleVideo_1280x720_10mb__240p.mp4
```
