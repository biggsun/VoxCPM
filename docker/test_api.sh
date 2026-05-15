#!/bin/bash

echo "=== Testing VoxCPM TTS API ==="
echo ""

BASE_URL="http://localhost:8000"

echo "1. Testing health endpoint..."
curl -s "${BASE_URL}/health" | jq .
echo ""

echo "2. Testing /v1/models endpoint..."
curl -s "${BASE_URL}/v1/models" | jq .
echo ""

echo "3. Testing /v1/audio/voices endpoint..."
curl -s "${BASE_URL}/v1/audio/voices" | jq .
echo ""

echo "4. Testing /v1/audio/speech (non-streaming)..."
curl -s "${BASE_URL}/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "voxcpm2",
    "input": "Hello, this is a test.",
    "voice": "alloy",
    "response_format": "mp3",
    "stream": false
  }' \
  --output test_output.mp3
ls -lh test_output.mp3
echo ""

echo "5. Testing /v1/audio/speech (streaming PCM)..."
curl -s "${BASE_URL}/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "voxcpm2",
    "input": "This is a streaming test.",
    "voice": "nova",
    "response_format": "pcm",
    "stream": true
  }' \
  --output test_stream.pcm
ls -lh test_stream.pcm
echo ""

echo "=== Tests completed ==="