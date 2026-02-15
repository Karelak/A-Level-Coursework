# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13.11
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

USER appuser
ARG MAILJET_API_KEY
ARG MAILJET_API_SECRET
ARG MAILJET_DEFAULT_SENDER
ARG PG_HOST
ARG PG_PORT
ARG PG_USER
ARG PG_PASSWORD
ARG PG_DB
COPY . .

# Copy and load environment variables
COPY .env .
RUN export $(cat .env | xargs)

EXPOSE 8000

CMD gunicorn wsgi:app --bind=0.0.0.0:8000
