import os
import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config import config, load_config
from .routes import speech_router, voices_router, models_router, health_router

os.environ["TOKENIZERS_PARALLELISM"] = "false"


def setup_logging():
    logging.basicConfig(
        level=config.logging.level,
        format=config.logging.format,
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def create_app():
    app = FastAPI(
        title="VoxCPM OpenAI-Compatible TTS API",
        description="OpenAI-compatible Text-to-Speech API powered by VoxCPM2",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(speech_router, tags=["speech"])
    app.include_router(voices_router, tags=["voices"])
    app.include_router(models_router, tags=["models"])
    app.include_router(health_router, tags=["health"])
    
    @app.on_event("startup")
    async def startup_event():
        logging.info(f"VoxCPM TTS API starting on {config.server.host}:{config.server.port}")
        logging.info(f"Model ID: {config.model.model_id}")
        logging.info(f"Cache Dir: {config.model.cache_dir}")
    
    return app


app = create_app()


def main():
    setup_logging()
    uvicorn.run(
        app,
        host=config.server.host,
        port=config.server.port,
        workers=config.server.workers,
    )


if __name__ == "__main__":
    main()