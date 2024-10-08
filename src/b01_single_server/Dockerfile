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
    --http-log-path=/var/log/nginx/access.log
RUN make && make install

RUN useradd -rU nginx
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log && \
    chown -R nginx:nginx /etc/nginx /var/log/nginx
USER nginx

CMD ["nginx", "-g", "daemon off;"]
