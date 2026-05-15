FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

LABEL maintainer="VoxCPM Team"
LABEL description="VoxCPM OpenAI-Compatible TTS API Server"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV TOKENIZERS_PARALLELISM=false
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3.10-venv \
    python3-pip \
    curl \
    git \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

RUN python3.10 -m pip install --no-cache-dir --upgrade pip setuptools wheel uv

WORKDIR /app

RUN uv pip install --system torch torchaudio --index-url https://download.pytorch.org/whl/cu121
RUN uv pip install --system fastapi uvicorn pyyaml pydantic soundfile scipy numpy

COPY . .

RUN uv pip install --system -e .

COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV VOXCPM_CONFIG_PATH=/app/docker/config.yaml

RUN mkdir -p /app/models /app/logs

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=60s --start-period=300s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
