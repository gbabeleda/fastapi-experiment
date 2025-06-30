# fastapi-experiment

## Description

This is a proof-of-concept repository to demonstrate the following:

- A demonstration of clean architecture with a fastapi backend application
- Backend application containerization with docker
- CI/CD deployment of containerized applications to "production" servers
- The use of code quality tools prior to the CI/CD pipeline like `pre-commit` and `ruff`
- Standardized local development setup, similar to how environments would be setup for teams specifically for vscode

## Local Development Setup

### Prerequisites

- [git](https://git-scm.com/)
- [uv](https://docs.astral.sh/uv/)
- [vscode](https://code.visualstudio.com/)
- [Docker](https://www.docker.com/)

### Create project via `uv`

```bash
uv init fastapi-experiment
```

### Add dependencies

```bash
uv add package --extra optional-dependency # dagster-cloud[serverless]
uv add package --optional optional-dependency-group # Add to [project.optional-dependencies] dev
```

### Install dependencies

```bash
uv sync --all-extras # For all dependency groups
uv sync --all-extras --no-extra ci # For all dependency groups excluding specific group
uv sync --extra dependency-group # For a specific group
uv sync --extra ci # Install ci on CI/CD
```

### Check dependencies

```bash
uv tree
```

### Activate pre-commit hooks

```bash
uv run pre-commit install
```

## FastAPI Application Workflows

### Non-Containerized (Optional)

#### Development

```bash
uv run uvicorn main:app --reload # Server auto-reload on code change
```

View the docs at `http://127.0.0.1:8000/docs`

#### Production

TO DO: Add CI/CD for non-containerized workflow

### Single Containerized Workflow

For this workflow, we use a `docker-compose.yaml` for local development, but deploy the application via docker CLI commands in the CI/CD pipeline.

> `.dockerignore` is the same for all containerized workflows.Exclude non-critical components from the Docker Image to improve built times

#### Development

`Dockerfile`

```Dockerfile
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
ADD . /app
WORKDIR /app
RUN uv sync --locked

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`docker-compose.yaml`

```yaml
services:
  fastapi:
    # Build using the Dockerfile in current directory
    build: .
    # Maps container port 8000 to host port 8000
    # Accessed via localholst:8000
    ports:
      - "8000:8000"
    volumes:
      # Mount local code into `/app` directory inside the container for hot reload
      - .:/app
    # Set environment vars in container
    env_file:
      - .env
    # Override Dockerfile CMD for development with hot reload
    command:
      [
        "uv",
        "run",
        "uvicorn",
        "main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--reload",
      ]
```

Run locally:

```bash
docker compose up
```

#### Production

`ci-cd.yaml`

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker
        uses: docker/setup-buildx-action@v3

      - name: Build image
        run: docker build -t my-fastapi-app:latest .

      - name: Run tests (optional)
        run: docker run --rm my-fastapi-app:latest uv run pytest # optional step

      - name: Push to Registry (optional)
        run: docker push my-fastapi-app:latest
```

### Multi-stage Dockerfile Workflow

This workflow uses a single Dockerfile with separate targets for dev and prod

`Dockerfile`

```Dockerfile
# Base setup (uv, deps)
FROM python:3.12-slim AS base
… install curl, uv, copy code, uv sync …

# Development image
FROM base AS dev
CMD ["uv","run","uvicorn","main:app","--host","0.0.0.0","--port","8000","--reload"]

# Production image
FROM base AS prod
CMD ["uv","run","uvicorn","main:app","--host","0.0.0.0","--port","8000"]

```

#### Development

`docker-compose.yaml`

```yaml
services:
  fastapi:
    build:
      context: .
      target: dev
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    env_file:
      - .env
```

Run locally:

```bash
docker compose up
```

#### Production

`ci-cd.yaml`

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      - name: Build prod image
        run: docker build --target prod -t my-fastapi-app:latest .
      - name: Run tests (optional)
        run: docker run --rm my-fastapi-app:latest uv run pytest
      - name: Push image
        run: docker push myregistry/my-fastapi-app:latest
```

## Versions

### Version 0.1.0
