import io
import numpy as np
import soundfile as sf
from typing import Optional
from scipy import signal


def numpy_to_pcm_bytes(audio: np.ndarray, sample_rate: int = 48000) -> bytes:
    audio_int16 = np.clip(audio * 32767, -32768, 32767).astype(np.int16)
    return audio_int16.tobytes()


def numpy_to_mp3_bytes(audio: np.ndarray, sample_rate: int = 48000) -> bytes:
    buffer = io.BytesIO()
    sf.write(buffer, audio, sample_rate, format='MP3')
    return buffer.getvalue()


def numpy_to_wav_bytes(audio: np.ndarray, sample_rate: int = 48000) -> bytes:
    buffer = io.BytesIO()
    sf.write(buffer, audio, sample_rate, format='WAV')
    return buffer.getvalue()


def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    if orig_sr == target_sr:
        return audio
    number_of_samples = round(len(audio) * float(target_sr) / orig_sr)
    resampled_audio = signal.resample(audio, number_of_samples)
    return resampled_audio


def convert_response_format(audio: np.ndarray, sample_rate: int, response_format: str) -> bytes:
    if response_format == "pcm":
        return numpy_to_pcm_bytes(audio, sample_rate)
    elif response_format == "mp3":
        return numpy_to_mp3_bytes(audio, sample_rate)
    elif response_format == "wav":
        return numpy_to_wav_bytes(audio, sample_rate)
    elif response_format == "opus":
        return numpy_to_mp3_bytes(audio, sample_rate)
    elif response_format == "aac":
        return numpy_to_mp3_bytes(audio, sample_rate)
    elif response_format == "flac":
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format='FLAC')
        return buffer.getvalue()
    else:
        return numpy_to_mp3_bytes(audio, sample_rate)