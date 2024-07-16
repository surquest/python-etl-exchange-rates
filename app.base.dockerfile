# FROM images.artifactory.dunnhumby.com/python:3.10-slim AS base
FROM python:3.11-slim AS base

# Update the base image
RUN apt update && apt full-upgrade -y

# Copy local code to the container image.
ENV PROJECT_DIR /opt/project
ENV SOURCE_DIR /opt/project/src
ENV TEST_DIR /opt/project/test
ENV HOME $PROJECT_DIR
RUN mkdir -p $PROJECT_DIR
WORKDIR $PROJECT_DIR

COPY /src/app.requirements.txt /tmp/app.requirements.txt

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV ENVIRONMENT DEV
ENV PYTHONUNBUFFERED True
ENV PYTHONPATH="${PYTHONPATH}:${SOURCE_DIR}:${TEST_DIR}"

# Install python packages
RUN pip install --no-cache-dir \
    -r /tmp/app.requirements.txt

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

FROM base AS test

COPY /test/test.requirements.txt /tmp/test.requirements.txt
RUN pip install --no-cache-dir -r /tmp/test.requirements.txt
ENV ENVIRONMENT TEST
WORKDIR $TEST_DIR


FROM base AS app

COPY src $PROJECT_DIR/src
COPY config $PROJECT_DIR/config

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
