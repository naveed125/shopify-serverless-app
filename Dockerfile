FROM python:3.8-slim-buster

WORKDIR /app

COPY app /app

COPY .aws /root/.aws

RUN pip install \
    chalice

