FROM python:3.10-slim-bullseye
RUN mkdir -p /app
COPY . /app
WORKDIR /app
RUN echo test_file_docker
RUN --mount=type=secret,id=creds,target=/app/.cred/creds.json
