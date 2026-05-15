from .speech import router as speech_router
from .voices import router as voices_router
from .models import router as models_router
from .health import router as health_router

__all__ = [
    "speech_router",
    "voices_router",
    "models_router",
    "health_router",
]