import os
import logging
from fastapi import APIRouter
from typing import List
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


def scan_reference_voices() -> List[VoiceInfo]:
    voices = [VoiceInfo(name="default", id="default", language="auto")]
    ref_dir = config.voices.reference_dir
    if not os.path.isdir(ref_dir):
        logger.warning(f"Reference voice directory does not exist: {ref_dir}")
        return voices
    extensions = set(config.voices.supported_extensions)
    seen = set()
    for filename in sorted(os.listdir(ref_dir)):
        name, ext = os.path.splitext(filename)
        if ext.lower() not in extensions:
            continue
        if name == "default" or name in seen:
            continue
        seen.add(name)
        voices.append(VoiceInfo(name=name, id=name, language="auto"))
    return voices


@router.get("/v1/audio/voices")
async def list_voices():
    logger.info("Listing available voices")
    voices = scan_reference_voices()
    return VoicesResponse(
        voices=voices,
        languages=config.languages,
    )
