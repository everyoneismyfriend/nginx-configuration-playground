FROM ubuntu:22.04

ARG NGINX_VERSION=1.26.0
ARG NGINX_DIR=/etc/nginx

WORKDIR /home
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y wget \
                       gcc \
                       make \
                       libpcre3-dev \
                       libssl-dev \
                       zlib1g-dev \
                       git && \
    wget http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz && \
    tar xzf nginx-${NGINX_VERSION}.tar.gz

ARG NGX_TRAFFIC_ACCOUNTING_GITLAB_TOKEN=""
ARG NGX_TRAFFIC_ACCOUNTING_GIT_BRANCH="main"
RUN git clone \
    -b ${NGX_TRAFFIC_ACCOUNTING_GIT_BRANCH} \
    https://oauth2:${NGX_TRAFFIC_ACCOUNTING_GITLAB_TOKEN}@gitlab.itglobal.com/cdn/traffic-accounting.git

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
    --add-module=/home/traffic-accounting
RUN make && make install

RUN useradd -rU nginx
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log && \
    chown -R nginx:nginx /etc/nginx /var/log/nginx
USER nginx

CMD ["nginx", "-g", "daemon off;"]
