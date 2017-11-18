FROM python:alpine3.6

LABEL maintainer="Zobkov Dmitry <dan0na@me.com>"

# PACKAGE INSTALLATION #

RUN set -ex \
# Install Nginx and supervisord
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

# CONFIGURATION #

# Copy config files
COPY ./config /config

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log \
# Make nginx run on the foreground
    && echo "daemon off;" >> /etc/nginx/nginx.conf \
# Remove default configuration from Nginx
    && rm /etc/nginx/conf.d/default.conf \
# Create directory for Nginx .pid file
    && mkdir -p /run/nginx \
# Move custom Nginx config
    && mv /config/nginx.conf /etc/nginx/conf.d \
# Create directories for uWSGI and supervisord configs
    && mkdir /etc/uwsgi /etc/supervisor.d \
# Move the base uWSGI ini file to enable default dynamic uwsgi process number
    && mv /config/uwsgi.ini /etc/uwsgi \
# Move custom Supervisord config
    && mv /config/supervisord.ini /etc/supervisor.d \
# Make the entrypoint executable
    && chmod +x /config/entrypoint.sh

# Exec the entrypoint that will generate Nginx additional configs
# Check this script for used ENV variables
ENTRYPOINT ["/config/entrypoint.sh"]

# Add demo app
COPY ./app /app
WORKDIR /app

# MAIN PROCESS EXEC #

# Restart this command if you override it
CMD ["/usr/bin/supervisord"]