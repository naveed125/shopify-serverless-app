FROM python:3.8-slim-buster

WORKDIR /app

COPY app /app

COPY aws/config /root/.aws/config

RUN pip install \
    chalice \
    httpie

