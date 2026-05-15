import io
import logging
import numpy as np
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from typing import Optional, List
import soundfile as sf

from ..config import config
from ..utils.audio import numpy_to_pcm_bytes, numpy_to_mp3_bytes, convert_response_format

logger = logging.getLogger(__name__)
router = APIRouter()

voxcpm_model = None


def get_model():
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


VOICE_DESCRIPTIONS = {
    "default": "",
    "alloy": "A neutral voice, balanced and clear",
    "echo": "A warm male voice, conversational and friendly",
    "fable": "A British voice, expressive and storytelling",
    "onyx": "A deep male voice, authoritative and confident",
    "nova": "A female voice, friendly and energetic",
    "shimmer": "A soft female voice, gentle and calm",
}


def build_control_instruction(voice: str, instructions: Optional[str]) -> str:
    base_instruction = VOICE_DESCRIPTIONS.get(voice, "")
    if instructions:
        if base_instruction:
            return f"{base_instruction}, {instructions}"
        return instructions
    return base_instruction


@router.post("/v1/audio/speech")
async def create_speech(request: SpeechRequest):
    logger.info(f"Speech request: model={request.model}, voice={request.voice}, stream={request.stream}, input={request.input[:50]}...")
    
    model = get_model()
    
    control_instruction = build_control_instruction(request.voice, request.instructions or request.instruct)
    
    text = request.input
    if control_instruction:
        text = f"({control_instruction}){text}"
    
    cfg_value = 2.0
    if request.speed != 1.0:
        if request.speed < 1.0:
            cfg_value = 1.5
        elif request.speed > 1.0:
            cfg_value = 2.5
    
    inference_timesteps = 10
    
    if request.stream:
        logger.info("Streaming mode enabled, returning PCM chunks")
        
        def generate_pcm_stream():
            try:
                for chunk in model.generate_streaming(
                    text=text,
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
            }
        )
    else:
        logger.info("Non-streaming mode, returning full audio")
        try:
            wav = model.generate(
                text=text,
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