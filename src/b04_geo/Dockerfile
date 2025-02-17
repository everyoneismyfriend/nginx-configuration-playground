FROM ubuntu:22.04

ARG NGINX_VERSION=1.26.0
WORKDIR /home
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y wget \
                       gcc \
                       make \
                       libpcre3-dev \
                       libssl-dev \
                       zlib1g-dev && \
    wget http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz && \
    tar xzf nginx-${NGINX_VERSION}.tar.gz

ARG NGX_HTTP_GEOIP2_MODULE_VERSION=3.4
WORKDIR /home/ngx-http-geoip2-module
RUN echo 'deb https://ppa.launchpadcontent.net/maxmind/ppa/ubuntu/ jammy main' >> /etc/apt/sources.list.d/maxmind-ubuntu-ppa-jammy.list && \
    apt-get install -y libmaxminddb0 \
                       libmaxminddb-dev \
                       mmdb-bin && \
    wget https://github.com/leev/ngx_http_geoip2_module/archive/refs/tags/${NGX_HTTP_GEOIP2_MODULE_VERSION}.tar.gz && \
    tar xzf ${NGX_HTTP_GEOIP2_MODULE_VERSION}.tar.gz

WORKDIR /home/nginx-${NGINX_VERSION}
RUN ./configure \
    --prefix=/etc/nginx \
    --user=nginx \
    --group=nginx \
    --sbin-path=/usr/sbin/nginx \
    --conf-path=/etc/nginx/nginx.conf \
    --pid-path=/etc/nginx/nginx.pid \
    --lock-path=/etc/nginx/nginx.lock \
    --error-log-path=/var/log/nginx/error.log \
    --http-log-path=/var/log/nginx/access.log \
    --with-http_realip_module \
    --add-module=/home/ngx-http-geoip2-module/ngx_http_geoip2_module-${NGX_HTTP_GEOIP2_MODULE_VERSION}
RUN make && make install

RUN wget https://git.io/GeoLite2-Country.mmdb && \
    mkdir -p /usr/share/GeoIP && \
    mv GeoLite2-Country.mmdb /usr/share/GeoIP

RUN useradd -rU nginx
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log && \
    chown -R nginx:nginx /etc/nginx /var/log/nginx
USER nginx

CMD ["nginx", "-g", "daemon off;"]
