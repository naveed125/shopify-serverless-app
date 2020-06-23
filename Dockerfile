FROM python:3.8-slim-buster

WORKDIR /app

COPY app /app

COPY .aws /root/.aws

RUN apt-get update \
&&  apt-get install -y curl

RUN pip install \
    chalice

