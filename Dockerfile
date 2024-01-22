FROM python:3.10-slim-bullseye
RUN mkdir -p /app
COPY . /app
WORKDIR /app
RUN echo test_file_docker
