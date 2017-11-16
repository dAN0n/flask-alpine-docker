## Supported tags and respective `Dockerfile` links

* [`python3.6`, `latest` _(Dockerfile)_](https://github.com/dAN0n/flask-alpine-docker/blob/master/python3.6/Dockerfile)

# flask-alpine
**Docker** image with **uWSGI** and **Nginx** for **Flask** web applications in **Python 3.6** running in a single container based on **Alpine Linux**.

This [**Docker**](https://www.docker.com/) image allows you to create [**Flask**](http://flask.pocoo.org/) web applications in [**Python**](https://www.python.org/) that run with [**uWSGI**](https://uwsgi-docs.readthedocs.org/en/latest/) and [**Nginx**](http://nginx.org/en/) in a single container.

This image is port of [**tiangolo/uwsgi-nginx-flask**](https://hub.docker.com/r/tiangolo/uwsgi-nginx-flask/) image on [**Alpine Linux**](https://alpinelinux.org/).

**GitHub repo**: <https://github.com/dAN0n/flask-alpine-docker/>

**Docker Hub image**: <https://hub.docker.com/r/dan0n/flask-alpine/>

## General Instructions

You don't have to clone this repo, you should be able to use this image as a base image for your project with something in your `Dockerfile` like:

```Dockerfile
FROM dan0n/flask-alpine

COPY ./app /app
```

Additional instructions you can see at [**base repository**](https://github.com/tiangolo/uwsgi-nginx-flask-docker/).
