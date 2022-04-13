FROM python:3.9-slim


# prevent apt-get install from prompting on certain packages
ENV DEBIAN_FRONTEND=noninteractive


COPY requirements.txt ./requirements.txt

RUN apt-get update && \
    apt-get install -y \
    build-essential \
    make \
    gcc \
    nginx \
    curl \
    && pip install --upgrade pip setuptools \
    && pip install -r requirements.txt \
    && apt-get remove -y --purge make gcc build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONIOENCODING=UTF-8

ENV PATH="/opt/program:${PATH}"

COPY * /opt/program/
COPY protopython/proto/query_pb2.py /opt/program/protopython/proto/query_pb2.py

COPY lib/* /opt/program/lib/
ENV PYTHONPATH="/opt/program/"
RUN chmod +x /opt/program/serve

WORKDIR /opt/program
