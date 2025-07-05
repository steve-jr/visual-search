# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.9.23

FROM python:${PYTHON_VERSION}-slim-bookworm

WORKDIR /app

RUN pip install --no-cache-dir torch==2.3.1+cpu torchvision==0.22.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Pre-copy only requirements first to leverage Docker cache
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]