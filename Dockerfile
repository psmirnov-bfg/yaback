FROM python:2.7-slim

RUN mkdir /app
WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app

WORKDIR /app/yaback

CMD python __main__.py
