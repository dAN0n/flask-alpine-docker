FROM python:alpine3.6

MAINTAINER Zobkov Dmitry <dan0na@me.com>

# PACKAGE INSTALLATION #

RUN set -ex \
# Install nginx and supervisord
    && apk add --no-cache --update \
        nginx \
        supervisor \
# Install build time dependencies
    && apk add --no-cache --virtual .build-deps \
        gcc \
        libc-dev \
        linux-headers \
# Update pip
    && pip install -U pip \
# Install flask and uWSGI
    && pip install flask uwsgi \
# Remove build time dependencies
    && apk del .build-deps \
# Remove cache files
    && rm -rf /var/cache/apk/*

# Using ports
EXPOSE 80 443

# NGINX CONFIGURATION #

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log \
# Make nginx run on the foreground
    && echo "daemon off;" >> /etc/nginx/nginx.conf \
# Remove default configuration from nginx
    && rm /etc/nginx/conf.d/default.conf \
# Create directory for .pid file
    && mkdir -p /run/nginx
# Copy the modified Nginx conf
COPY nginx.conf /etc/nginx/conf.d/
# By default, allow unlimited file sizes, modify it to limit the file sizes
ENV NGINX_MAX_UPLOAD 0

# URL under which static (not modified by Python) files will be requested
# They will be served by Nginx directly, without being handled by uWSGI
ENV STATIC_URL /static
# Absolute path in where the static files will be
ENV STATIC_PATH /app/static
# If STATIC_INDEX is 1, serve / with /static/index.html directly (or the static URL configured)
ENV STATIC_INDEX 0

# Copy the entrypoint that will generate Nginx additional configs
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# uWSGI CONFIGURATION #

# Copy the base uWSGI ini file to enable default dynamic uwsgi process number
COPY uwsgi_base.ini /etc/uwsgi/uwsgi.ini
# Which uWSGI .ini file should be used, to make it customizable
ENV UWSGI_INI /app/uwsgi.ini

# Add demo app
COPY ./app /app
WORKDIR /app

# SUPERVISORD CONFIGURATION #

# Custom Supervisord config
COPY supervisord.conf /etc/supervisor.d/supervisord.ini

CMD ["/usr/bin/supervisord"]