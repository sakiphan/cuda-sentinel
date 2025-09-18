# CUDA Sentinel Docker Image - Lightweight version
FROM ubuntu:22.04

# Metadata
LABEL maintainer="CUDA Sentinel Contributors"
LABEL description="GPU Health & Benchmark Toolkit"
LABEL version="0.1.0"

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=all
ENV NVIDIA_VISIBLE_DEVICES=all

# System updates and basic packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create Python symlink
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy Python dependencies and install
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Install Python package in editable mode
RUN pip3 install -e .

# Enable NVIDIA runtime capabilities
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Expose Prometheus metrics port
EXPOSE 8080

# Container health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD cuda-sentinel health --json || exit 1

# Default command: Prometheus exporter
CMD ["cuda-sentinel", "exporter", "--format", "prometheus", "--port", "8080", "--host", "0.0.0.0"]

# Usage:
# docker build --tag cuda-sentinel .
# docker run --gpus all -p 8080:8080 cuda-sentinel
