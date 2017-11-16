FROM python:alpine3.6

MAINTAINER Zobkov Dmitry <dan0na@me.com>

# Upgrade pip
RUN pip install -U pip

# Install uWSGI, nginx and supervisord
RUN set -ex \
    && apk add --no-cache --update \
        nginx \
        supervisor \
    && apk add --no-cache --virtual .build-deps \
        gcc \
        libc-dev \
        linux-headers \
    && pip install uwsgi \
    && apk del .build-deps \
    && rm -rf /var/cache/apk/*

# Install mysqlclient using mariadb-dev client libs
RUN set -ex \
    && apk add --no-cache --virtual .build-deps \
        gcc \
        libc-dev \
        linux-headers \
        mariadb-dev \
    && pip install mysqlclient \
    && cp /usr/lib/libmysqlclient.a /usr/lib/libmysqlclient.so.18.0.0 /usr/bin/mysql_config /tmp \
    && cp -ar /usr/include/mysql /tmp \
    && apk del .build-deps \
    && mv /tmp/libmysqlclient.a /tmp/libmysqlclient.so.18.0.0 /usr/lib \
    && mv /tmp/mysql /usr/include/mysql \
    && mv /tmp/mysql_config /usr/bin \
    && ln -s /usr/lib/libmysqlclient.so.18.0.0 /usr/lib/libmysqlclient.so.18 \
    && ln -s /usr/lib/libmysqlclient.so.18 /usr/lib/libmysqlclient.so \
    && ln -s /usr/lib/libmysqlclient.so /usr/lib/libmysqlclient_r.so \
    && ln -s /usr/lib/libmysqlclient.a /usr/lib/libmysqlclient_r.a

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# Using ports
EXPOSE 80 443

# NGINX CONFIGURATION #

# Make nginx run on the foreground
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
# Remove default configuration from nginx
RUN rm /etc/nginx/conf.d/default.conf
# Copy the modified Nginx conf
COPY nginx.conf /etc/nginx/conf.d/
# Create directory for .pid file
RUN mkdir -p /run/nginx
# By default, allow unlimited file sizes, modify it to limit the file sizes
ENV NGINX_MAX_UPLOAD 0

# Copy the entrypoint that will generate Nginx additional configs
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# URL under which static (not modified by Python) files will be requested
# They will be served by Nginx directly, without being handled by uWSGI
ENV STATIC_URL /static
# Absolute path in where the static files will be
ENV STATIC_PATH /app/static
# If STATIC_INDEX is 1, serve / with /static/index.html directly (or the static URL configured)
ENV STATIC_INDEX 0

# uWSGI CONFIGURATION #

# Copy the base uWSGI ini file to enable default dynamic uwsgi process number
COPY uwsgi_base.ini /etc/uwsgi/uwsgi.ini
# Which uWSGI .ini file should be used, to make it customizable
ENV UWSGI_INI /app/uwsgi.ini

# FLASK CONFIGURATION #

# Copy requirements.txt file
COPY app/requirements.txt /tmp/
# Install required python packages
RUN pip install -r /tmp/requirements.txt

# APP CONFIGURATION #

# Set secret key for application
ARG FLASK_APP_SECRET_KEY
ENV FLASK_APP_SECRET_KEY ${FLASK_APP_SECRET_KEY:-}
# Set database path for application
ARG DATABASE_URL
ENV DATABASE_URL ${DATABASE_URL:-}

# Add demo app
COPY ./app /app
WORKDIR /app

# Upgrade database
# RUN python db.py upgrade

# SUPERVISORD CONFIGURATION #

# Custom Supervisord config
# COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY supervisord.conf /etc/supervisor.d/supervisord.ini

CMD ["/usr/bin/supervisord"]