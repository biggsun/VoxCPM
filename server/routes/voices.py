import logging
from fastapi import APIRouter
from typing import List, Dict
from pydantic import BaseModel

from ..config import config

logger = logging.getLogger(__name__)
router = APIRouter()


class VoiceInfo(BaseModel):
    name: str
    id: str
    language: str = "auto"


class VoicesResponse(BaseModel):
    voices: List[VoiceInfo]
    languages: List[str]


@router.get("/v1/audio/voices")
async def list_voices():
    logger.info("Listing available voices")
    
    voices = []
    for voice_config in config.voices.preset:
        voices.append(VoiceInfo(
            name=voice_config.name,
            id=voice_config.name,
            language="auto"
        ))
    
    return VoicesResponse(
        voices=voices,
        languages=config.languages
    )