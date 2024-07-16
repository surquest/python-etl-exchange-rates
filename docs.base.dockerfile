FROM python:3.11-slim

# Build-time flags
ARG WITH_PLUGINS=true

# Environment variables
ENV PACKAGES=/usr/local/lib/python3.11/site-packages
ENV PYTHONDONTWRITEBYTECODE=1

# Install dependencies
COPY docs.requirements.txt /tmp/docs.requirements.txt
RUN pip install -r /tmp/docs.requirements.txt

# Set working directory
ENV DOCS_DIR="/opt/project/docs"
WORKDIR $DOCS_DIR

# Expose MkDocs development server port
EXPOSE 8000