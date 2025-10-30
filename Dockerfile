FROM python:3.12.7-bullseye

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y pkg-config python3-dev default-libmysqlclient-dev build-essential make

WORKDIR /work
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .


CMD ["make", "db_reset", "run"]
