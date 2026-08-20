# Multi-Stage Production Dockerfile for Stateful Multi-Agent Research Orchestrator
FROM python:3.11-slim as base

WORKDIR /app

# Prevent Python from writing bytecode
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose ports for FastAPI (8000) and Frontend (3000)
EXPOSE 8000
EXPOSE 3000

# Default command launches FastAPI backend
CMD ["uvicorn", "5_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
