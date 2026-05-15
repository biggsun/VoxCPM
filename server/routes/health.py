import logging
from fastapi import APIRouter
from pydantic import BaseModel
import torch

logger = logging.getLogger(__name__)
router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    gpu_available: bool
    gpu_count: int


@router.get("/health")
async def health_check():
    logger.debug("Health check requested")

    gpu_available = torch.cuda.is_available()
    gpu_count = torch.cuda.device_count() if gpu_available else 0

    from .speech import voxcpm_model
    model_loaded = voxcpm_model is not None

    if model_loaded and gpu_available:
        status = "healthy"
    elif model_loaded:
        status = "healthy_no_gpu"
    else:
        status = "loading"

    return HealthResponse(
        status=status,
        model_loaded=model_loaded,
        gpu_available=gpu_available,
        gpu_count=gpu_count
    )
