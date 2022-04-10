# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
ARG DEBUG
ARG SECRET_KEY
ARG DJANGO_ALLOWED_HOSTS
ARG API_KEY
