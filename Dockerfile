FROM python:3.8.5-alpine3.12

RUN mkdir -p /opt/service

WORKDIR /opt/service

RUN apk add --no-cache git

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY setup.py .
COPY lib lib

ENV PYTHONPATH "/opt/service/lib:${PYTHONPATH}"
