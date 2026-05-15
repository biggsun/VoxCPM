# VoxCPM OpenAI-Compatible TTS API

OpenAI-compatible Text-to-Speech API server powered by VoxCPM2.

## Features

- **OpenAI API Compatible**: Drop-in replacement for OpenAI's `/v1/audio/speech` endpoint
- **Streaming Support**: Real-time PCM audio streaming
- **Multi-format Output**: MP3, WAV, FLAC, PCM formats
- **Voice Design**: Create voices from natural language descriptions
- **30 Languages**: Support for 30 languages including Chinese, English, Japanese, etc.
- **GPU Accelerated**: NVIDIA CUDA support for fast inference

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/OpenBMB/VoxCPM.git
cd VoxCPM
```

### 2. Deploy with Docker Compose

```bash
cd docker
docker-compose up -d
```

The server will start on port 8000 (configurable via `PORT` environment variable).

### 3. Verify Deployment

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "gpu_available": true,
  "gpu_count": 1
}
```

## API Endpoints

### POST /v1/audio/speech

Generate speech from text.

**Request Body:**
```json
{
  "model": "voxcpm2",
  "input": "Hello, world!",
  "voice": "alloy",
  "response_format": "mp3",
  "stream": false,
  "speed": 1.0,
  "instructions": "A warm female voice"
}
```

**Parameters:**
- `model`: Model ID (default: "voxcpm2")
- `input`: Text to synthesize
- `voice`: Voice preset (default/alloy/echo/fable/onyx/nova/shimmer)
- `response_format`: Output format (mp3/wav/pcm/flac)
- `stream`: Enable streaming (true/false)
- `speed`: Speech speed (0.25-4.0)
- `instructions`: Voice description for Voice Design

**Non-streaming Example:**
```bash
curl http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"voxcpm2","input":"Hello!","voice":"alloy"}' \
  --output speech.mp3
```

**Streaming Example:**
```bash
curl http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"voxcpm2","input":"Hello!","voice":"alloy","stream":true,"response_format":"pcm"}' \
  --output speech.pcm
```

### GET /v1/audio/voices

List available voices.

```bash
curl http://localhost:8000/v1/audio/voices
```

Response:
```json
{
  "voices": [
    {"name": "default", "id": "default", "language": "auto"},
    {"name": "alloy", "id": "alloy", "language": "auto"},
    ...
  ],
  "languages": ["Auto", "Chinese", "English", ...]
}
```

### GET /v1/models

List available models.

```bash
curl http://localhost:8000/v1/models
```

Response:
```json
{
  "object": "list",
  "data": [
    {
      "id": "voxcpm2",
      "object": "model",
      "created": 1234567890,
      "owned_by": "openbmb"
    }
  ]
}
```

### GET /health

Health check endpoint.

```bash
curl http://localhost:8000/health
```

## Voice Presets

| Voice | Description |
|-------|-------------|
| default | Default voice |
| alloy | Neutral voice, balanced and clear |
| echo | Male voice, warm and conversational |
| fable | British voice, expressive and storytelling |
| onyx | Deep male voice, authoritative and confident |
| nova | Female voice, friendly and energetic |
| shimmer | Soft female voice, gentle and calm |

## Voice Design

Use the `instructions` parameter to create custom voices:

```json
{
  "input": "Hello!",
  "instructions": "A young girl with a soft, sweet voice"
}
```

## Configuration

Edit `docker/config.yaml` to customize settings:

```yaml
server:
  host: "0.0.0.0"
  port: 8000

model:
  model_id: "openbmb/VoxCPM2"
  cache_dir: "/app/models"
  optimize: true
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| PORT | Server port | 8000 |
| VOXCPM_CONFIG_PATH | Config file path | /app/docker/config.yaml |

## Requirements

- Docker 19.03+
- Docker Compose 1.27+
- NVIDIA Docker (nvidia-container-toolkit)
- CUDA-capable GPU (recommended: RTX 3090/4090 or better)
- 16GB+ RAM
- 30GB+ disk space for model cache

## Model Download

The model (~2B parameters) will be automatically downloaded on first startup from HuggingFace:
- Model ID: `openbmb/VoxCPM2`
- Download time: ~10-15 minutes (depending on network)
- Model cache: `/app/models` (persistent volume)

## Troubleshooting

### Model Loading Slow
- First startup downloads the model (~30GB)
- Check network connection to HuggingFace
- Model cached in Docker volume `voxcpm-models-cache`

### GPU Not Detected
- Install nvidia-container-toolkit
- Verify GPU visibility: `docker run --gpus all nvidia/cuda:12.1 nvidia-smi`

### Out of Memory
- VoxCPM2 requires ~8GB VRAM
- Reduce batch size or use smaller model

## License

Apache-2.0 License. See [LICENSE](LICENSE) for details.