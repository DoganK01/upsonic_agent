# syntax=docker/dockerfile:1.4

    FROM python:3.13-slim AS builder

    COPY --from=ghcr.io/astral-sh/uv:0.7.21 /uv /uvx /usr/local/bin/
    
    WORKDIR /tmp/build
    
    COPY pyproject.toml uv.lock /tmp/build/
    
    RUN --mount=type=cache,target=/root/.cache/uv \
        uv venv && \
        uv sync --frozen --no-install-project --no-dev
    
    FROM python:3.13-slim
    
    COPY --from=builder /tmp/build/.venv /opt/venv
    
    ENV PATH="/opt/venv/bin:$PATH"
    
    WORKDIR /app
    
    
    CMD ["python", "-m", "src.app.agent"]
