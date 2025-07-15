# syntax=docker/dockerfile:1.4

# --- Stage 1: Builder Stage ---
    FROM python:3.13-slim AS builder

    # Copy uv binary from its official image.
    COPY --from=ghcr.io/astral-sh/uv:0.7.21 /uv /uvx /usr/local/bin/
    
    # Set a temporary working directory for dependency installation
    WORKDIR /tmp/build
    
    # Copy only dependency definition files to leverage Docker caching
    COPY pyproject.toml uv.lock /tmp/build/
    
    # Install all dependencies with uv into a virtual environment within the builder stage.
    # We'll install it into /tmp/build/.venv so it's isolated from /app.
    # Use a cache mount for faster rebuilds of dependencies.
    RUN --mount=type=cache,target=/root/.cache/uv \
        uv venv && \
        uv sync --frozen --no-install-project --no-dev
    
    # --- Stage 2: Production Stage ---
    FROM python:3.13-slim
    
    # Copy the virtual environment from the builder stage to a *non-mounted* location.
    # /opt/venv is a common conventional location for application-specific venvs.
    COPY --from=builder /tmp/build/.venv /opt/venv
    
    # Set the PATH to include the virtual environment's bin directory.
    # This makes executables from your dependencies directly runnable.
    ENV PATH="/opt/venv/bin:$PATH"
    
    # Set the main working directory for your application code.
    # This is where your code from the bind mount will appear.
    WORKDIR /app
    
    # The Dockerfile's `COPY . /app/` line for application code can be removed
    # if you are *always* using `volumes: - .:/app` in docker-compose.
    # However, keeping it makes the image runnable stand-alone without docker-compose.
    # If you keep it, be aware the bind mount will override it.
    # For robustness in a development setup with volumes, remove this `COPY . /app/` here.
    # COPY . /app/ # REMOVE THIS LINE IF YOU ARE USING - .:/app IN DOCKER-COMPOSE.YML
    
    # Activate environment and run the app
    CMD ["python", "-m", "src.app.agent"]