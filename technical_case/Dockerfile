FROM python:3.10-bullseye

RUN apt-get update && apt-get install --no-install-recommends -y \
    gcc \
    build-essential \
    && rm -rf /var/cache/apt/* /var/lib/apt/lists/*

RUN adduser --system --disabled-password -u 1000 docker_user
RUN passwd -d docker_user

RUN apt-get update && apt-get install --no-install-recommends -y \
	sudo \
	gdal-bin

RUN adduser docker_user sudo

WORKDIR /home/docker_user

COPY ./requirements.txt requirements.txt

RUN pip install --upgrade pip && \
	pip install --no-cache-dir -r requirements.txt

COPY ./gis_api gis_api

RUN chown -R docker_user /home/docker_user

USER docker_user

WORKDIR /home/docker_user/gis_api