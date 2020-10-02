FROM python:3.8
FROM tiangolo/meinheld-gunicorn:python3.8

RUN mkdir /code
RUN mkdir /code/src
WORKDIR /code
COPY . ./src

RUN pip install -r ./src/auth/requirements.txt