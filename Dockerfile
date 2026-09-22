FROM python:3.14.3

ENV PYTHONDONTWRITEBYCODE 1
ENV PYTHONBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY . .