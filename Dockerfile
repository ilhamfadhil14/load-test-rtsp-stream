FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

# Install system dependencies including build tools for psutil
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy uv project files first for better caching
COPY pyproject.toml .
COPY uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy source code
COPY src/ ./src/

# Copy config files
COPY config/config.docker.yaml ./config/config.yaml

# Create directories
RUN mkdir -p logs

# Wait for MediaMTX and run the load tester
CMD ["sh", "-c", "sleep 5 && uv run python -m rtsp_load_tester.main --skip-prompt"]
