# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.9.23

FROM python:${PYTHON_VERSION}-slim-bookworm

WORKDIR /app

# Pre-copy only requirements first to leverage Docker cache
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]