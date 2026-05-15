import logging
from fastapi import APIRouter
from typing import List, Dict
from pydantic import BaseModel
import time

from ..config import config

logger = logging.getLogger(__name__)
router = APIRouter()


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "openbmb"


class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]


@router.get("/v1/models")
async def list_models():
    logger.info("Listing available models")
    
    model_id = config.model.model_id
    if "/" in model_id:
        model_name = model_id.split("/")[-1]
    else:
        model_name = model_id
    
    models = [
        ModelInfo(
            id="voxcpm2",
            object="model",
            created=int(time.time()),
            owned_by="openbmb"
        )
    ]
    
    return ModelsResponse(
        object="list",
        data=models
    )