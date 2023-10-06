FROM python:3.11-slim-buster

RUN pip install poetry


COPY poetry.lock pyproject.toml /

RUN poetry install --without dev

ENV PYTHONPATH=/app:$PYTHONPATH

COPY src/ /app/
WORKDIR /app
