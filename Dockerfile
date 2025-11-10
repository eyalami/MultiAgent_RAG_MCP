FROM python:3.11-slim AS builder

# Set workdir
WORKDIR /app

# Install build dependencies with immediate cleanup in same layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        procps \
        git curl ca-certificates gnupg \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /var/cache/apt/*

# Install Python packages in builder with cleanup
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt && \
    rm -rf /root/.cache/pip/*

# Download model in builder
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Final stage with minimal image
FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /root/.cache/huggingface /root/.cache/huggingface

# Create cache directories with appropriate permissions in one layer
RUN mkdir -p /root/.cache/huggingface data/cache && \
    chmod -R 777 /root/.cache

# Copy application files
COPY src ./src
COPY data ./data
COPY .mcp /app/.mcp
COPY gunicorn_conf.py ./gunicorn_conf.py

# Set environment variables
ENV PATH=/root/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_CACHE=/app/data/cache/transformers \
    HF_HOME=/app/data/cache/huggingface 
    # TAVILY_API_KEY=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

# Install Node.js + MCP tools
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates gnupg tini \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get update \
    && apt-get install -y nodejs \
    && npm install -g mcp-remote \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/* \
    && apt-get clean

# Set tini as entrypoint
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD sh -c "\
     echo 'Starting preprocessing...' && \
     python -m src.scripts.preprocess_kb && \
     echo 'Starting FastAPI server...' && \
     exec gunicorn src.main:app \
     -k uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:80 \
     --workers=${WORKERS:-1} \
     --threads=${THREADS:-1} \
     --timeout=${TIMEOUT:-300} \
     --access-logfile=- \
     --error-logfile=- \
     --log-level debug \
     --capture-output \
     -c gunicorn_conf.py"

