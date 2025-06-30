# uv implementation using uv installer
FROM python:3.12-slim-bookworm

# Install curl and certificates
# Remove package manager cache files after installation
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Download and run uv installer
ADD https://astral.sh/uv/0.7.7/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
# Ensure the installed binary is on the PATH
ENV PATH="/root/.local/bin/:$PATH"

# Copy the project and install dependencies
# Excludes stuff in .dockerignore
ADD . /app
WORKDIR /app
RUN uv sync --locked

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
