import io
import os
import logging
import numpy as np
from fastapi import APIRouter
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from typing import Optional
import soundfile as sf

from ..config import config
from ..utils.audio import numpy_to_pcm_bytes, numpy_to_mp3_bytes, convert_response_format

logger = logging.getLogger(__name__)
router = APIRouter()

voxcpm_model = None


def load_model():
    global voxcpm_model
    if voxcpm_model is None:
        import voxcpm
        logger.info(f"Loading VoxCPM model: {config.model.model_id}")
        voxcpm_model = voxcpm.VoxCPM.from_pretrained(
            config.model.model_id,
            load_denoiser=config.model.load_denoiser,
            optimize=config.model.optimize,
            cache_dir=config.model.cache_dir,
        )
        logger.info("VoxCPM model loaded successfully")
    return voxcpm_model


def get_model():
    if voxcpm_model is None:
        raise RuntimeError("Model not loaded. Server is still starting up.")
    return voxcpm_model


class SpeechRequest(BaseModel):
    model: str = "voxcpm2"
    input: str
    voice: str = "default"
    response_format: str = "mp3"
    speed: float = 1.0
    stream: bool = False
    language: Optional[str] = "Auto"
    instructions: Optional[str] = None
    instruct: Optional[str] = None


def resolve_reference_audio(voice: str) -> Optional[str]:
    if voice == "default":
        return None
    ref_dir = config.voices.reference_dir
    if not os.path.isdir(ref_dir):
        return None
    extensions = config.voices.supported_extensions
    for ext in extensions:
        candidate = os.path.join(ref_dir, voice + ext)
        if os.path.isfile(candidate):
            return candidate
    return None


def speed_to_cfg(speed: float) -> float:
    if speed <= 0.25:
        return 1.0
    elif speed >= 4.0:
        return 4.0
    elif speed == 1.0:
        return 2.0
    else:
        return 1.0 + (speed - 0.25) * (3.0 / 3.75)


@router.post("/v1/audio/speech")
async def create_speech(request: SpeechRequest):
    logger.info(f"Speech request: model={request.model}, voice={request.voice}, stream={request.stream}, input={request.input[:50]}...")

    model = get_model()

    reference_wav_path = resolve_reference_audio(request.voice)

    if reference_wav_path is None and request.voice != "default":
        logger.warning(f"Voice '{request.voice}' not found in reference directory, falling back to default")

    text = request.input
    if request.instructions or request.instruct:
        instruction = request.instructions or request.instruct
        text = f"({instruction}){text}"

    cfg_value = speed_to_cfg(request.speed)
    inference_timesteps = 10

    if request.stream:
        logger.info("Streaming mode enabled, returning PCM chunks")

        def generate_pcm_stream():
            try:
                for chunk in model.generate_streaming(
                    text=text,
                    reference_wav_path=reference_wav_path,
                    cfg_value=cfg_value,
                    inference_timesteps=inference_timesteps,
                ):
                    pcm_bytes = numpy_to_pcm_bytes(chunk, model.tts_model.sample_rate)
                    yield pcm_bytes
            except Exception as e:
                logger.error(f"Error in streaming generation: {e}")
                raise

        return StreamingResponse(
            generate_pcm_stream(),
            media_type="application/octet-stream",
            headers={
                "Content-Type": "audio/pcm",
                "X-Content-Type-Options": "nosniff",
                "X-Sample-Rate": str(model.tts_model.sample_rate),
                "X-Bits-Per-Sample": "16",
                "X-Channels": "1",
                "X-Audio-Format": "pcm_s16le",
            }
        )
    else:
        logger.info("Non-streaming mode, returning full audio")
        try:
            wav = model.generate(
                text=text,
                reference_wav_path=reference_wav_path,
                cfg_value=cfg_value,
                inference_timesteps=inference_timesteps,
            )

            audio_bytes = convert_response_format(
                wav,
                model.tts_model.sample_rate,
                request.response_format
            )

            content_type = "audio/mpeg" if request.response_format == "mp3" else f"audio/{request.response_format}"

            return Response(
                content=audio_bytes,
                media_type=content_type,
                headers={
                    "Content-Disposition": f"attachment; filename=speech.{request.response_format}"
                }
            )
        except Exception as e:
            logger.error(f"Error in non-streaming generation: {e}")
            raise
