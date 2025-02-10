# Use a minimal base image
FROM --platform=linux/amd64 python:3.11-slim

# Set environment variables early to optimize caching
ENV POETRY_VERSION=1.8.3 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_IN_PROJECT=1 \
  POETRY_VIRTUALENVS_CREATE=1 \
  POETRY_CACHE_DIR=/tmp/poetry_cache \
  VIRTUAL_ENV=/app/.venv \
  PATH="/app/.venv/bin:$PATH"

# Install dependencies (use --no-install-recommends to reduce image size)
RUN apt-get update && apt-get install -y --no-install-recommends \
  wget \
  unzip \
  curl \
  && wget -qO /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
  && apt-get install -y --no-install-recommends /tmp/google-chrome.deb \
  && rm -rf /tmp/google-chrome.deb \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

# Set working directory
WORKDIR /app

# Copy only necessary files first (to leverage Docker's cache)
COPY pyproject.toml poetry.lock ./

# Install dependencies separately before adding the source code
RUN poetry install --no-root --no-cache

# Copy source code
COPY src/ ./src

# Use a non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Set entrypoint
ENTRYPOINT [ "python", "src/main.py"]

