import requests
import json
import os

BASE_URL = "http://localhost:8000"


def test_health():
    print("Testing /health...")
    resp = requests.get(f"{BASE_URL}/health")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    assert resp.status_code == 200
    print("✓ Health check passed\n")


def test_models():
    print("Testing /v1/models...")
    resp = requests.get(f"{BASE_URL}/v1/models")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    assert resp.status_code == 200
    print("✓ Models endpoint passed\n")


def test_voices():
    print("Testing /v1/audio/voices...")
    resp = requests.get(f"{BASE_URL}/v1/audio/voices")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    assert resp.status_code == 200
    print("✓ Voices endpoint passed\n")


def test_speech_non_stream():
    print("Testing /v1/audio/speech (non-streaming)...")
    payload = {
        "model": "voxcpm2",
        "input": "Hello, this is a test message from VoxCPM.",
        "voice": "alloy",
        "response_format": "mp3",
        "stream": False
    }
    resp = requests.post(
        f"{BASE_URL}/v1/audio/speech",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    print(f"Status: {resp.status_code}")
    print(f"Content-Type: {resp.headers.get('Content-Type')}")
    
    if resp.status_code == 200:
        os.makedirs("test_output", exist_ok=True)
        output_file = "test_output/non_stream.mp3"
        with open(output_file, "wb") as f:
            f.write(resp.content)
        print(f"Saved to: {output_file}")
        print(f"File size: {len(resp.content)} bytes")
        print("✓ Non-streaming speech passed\n")
    else:
        print(f"Error: {resp.text}")
        raise Exception("Speech generation failed")


def test_speech_stream():
    print("Testing /v1/audio/speech (streaming)...")
    payload = {
        "model": "voxcpm2",
        "input": "This is a streaming test message.",
        "voice": "nova",
        "response_format": "pcm",
        "stream": True
    }
    resp = requests.post(
        f"{BASE_URL}/v1/audio/speech",
        headers={"Content-Type": "application/json"},
        json=payload,
        stream=True
    )
    print(f"Status: {resp.status_code}")
    print(f"Content-Type: {resp.headers.get('Content-Type')}")
    
    if resp.status_code == 200:
        os.makedirs("test_output", exist_ok=True)
        output_file = "test_output/stream.pcm"
        chunks = []
        for chunk in resp.iter_content(chunk_size=4096):
            if chunk:
                chunks.append(chunk)
        
        with open(output_file, "wb") as f:
            f.write(b"".join(chunks))
        
        print(f"Received {len(chunks)} chunks")
        print(f"Saved to: {output_file}")
        print(f"File size: {sum(len(c) for c in chunks)} bytes")
        print("✓ Streaming speech passed\n")
    else:
        print(f"Error: {resp.text}")
        raise Exception("Speech streaming failed")


if __name__ == "__main__":
    print("=" * 50)
    print("VoxCPM TTS API Test Suite")
    print("=" * 50 + "\n")
    
    try:
        test_health()
        test_models()
        test_voices()
        test_speech_non_stream()
        test_speech_stream()
        
        print("=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)