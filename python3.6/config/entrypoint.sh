#!/bin/sh
set -e

# By default, allow unlimited file sizes, modify it to limit the file sizes
NGINX_MAX_UPLOAD=${NGINX_MAX_UPLOAD:-0}
# URL under which static (not modified by Python) files will be requested
# They will be served by Nginx directly, without being handled by uWSGI
STATIC_URL=${STATIC_URL:-'/static'}
# Absolute path in where the static files will be
STATIC_PATH=${STATIC_PATH:-'/app/static'}
# If STATIC_INDEX is 1, serve / with /static/index.html directly (or the static URL configured)
STATIC_INDEX=${STATIC_INDEX:-0}

# Set maximum upload file size
sed -i -E "s/(client_max_body_size) 1m;/\1 $NGINX_MAX_UPLOAD;/" /etc/nginx/nginx.conf

# Generate Nginx config first part using the environment variables
echo 'server {
    location / {
        try_files $uri @app;
    }
    location @app {
        include uwsgi_params;
        uwsgi_pass unix:///tmp/uwsgi.sock;
    }
    '"location $STATIC_URL {
        alias $STATIC_PATH;
    }" > /etc/nginx/conf.d/nginx.conf

# If STATIC_INDEX is 1, serve / with /static/index.html directly (or the static URL configured)
if [[ $STATIC_INDEX == 1 ]] ; then 
echo "    location = / {
        index $STATIC_URL/index.html;
    }" >> /etc/nginx/conf.d/nginx.conf
fi
# Finish the Nginx config file
echo "}" >> /etc/nginx/conf.d/nginx.conf

exec "$@"