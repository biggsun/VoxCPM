#!/bin/bash
set -e

CONFIG_PATH="${VOXCPM_CONFIG_PATH:-/app/docker/config.yaml}"
export VOXCPM_CONFIG_PATH="$CONFIG_PATH"

SERVER_PORT=$(python3.10 -c "
import yaml, os
config_path = os.environ.get('VOXCPM_CONFIG_PATH', '/app/docker/config.yaml')
try:
    with open(config_path) as f:
        c = yaml.safe_load(f)
    print(c.get('server', {}).get('port', 8000))
except:
    print(8000)
")

SERVER_HOST=$(python3.10 -c "
import yaml, os
config_path = os.environ.get('VOXCPM_CONFIG_PATH', '/app/docker/config.yaml')
try:
    with open(config_path) as f:
        c = yaml.safe_load(f)
    print(c.get('server', {}).get('host', '0.0.0.0'))
except:
    print('0.0.0.0')
")

echo "Starting VoxCPM TTS API on ${SERVER_HOST}:${SERVER_PORT}"
echo "Config: ${CONFIG_PATH}"

exec python3.10 -m uvicorn server.app:app \
    --host "${SERVER_HOST}" \
    --port "${SERVER_PORT}" \
    ${UVICORN_EXTRA_ARGS:-}
