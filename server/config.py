import os
import yaml
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1


class ModelConfig(BaseModel):
    model_id: str = "openbmb/VoxCPM2"
    cache_dir: str = "/app/models"
    load_denoiser: bool = False
    optimize: bool = True


class AudioConfig(BaseModel):
    sample_rate: int = 48000
    default_voice: str = "default"
    default_speed: float = 1.0
    default_language: str = "Auto"


class VoiceConfig(BaseModel):
    name: str
    description: str


class VoicesConfig(BaseModel):
    preset: List[VoiceConfig]


class LoggingConfig(BaseModel):
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class AppConfig(BaseModel):
    server: ServerConfig
    model: ModelConfig
    audio: AudioConfig
    voices: VoicesConfig
    languages: List[str]
    logging: LoggingConfig


def load_config(config_path: Optional[str] = None) -> AppConfig:
    if config_path is None:
        config_path = os.environ.get("VOXCPM_CONFIG_PATH", "/app/server/config.yaml")
    
    if not os.path.exists(config_path):
        default_config = {
            "server": {"host": "0.0.0.0", "port": 8000, "workers": 1},
            "model": {"model_id": "openbmb/VoxCPM2", "cache_dir": "/app/models", "load_denoiser": False, "optimize": True},
            "audio": {"sample_rate": 48000, "default_voice": "default", "default_speed": 1.0, "default_language": "Auto"},
            "voices": {
                "preset": [
                    {"name": "default", "description": "Default voice"},
                    {"name": "alloy", "description": "Neutral voice"},
                    {"name": "echo", "description": "Male voice"},
                    {"name": "fable", "description": "British voice"},
                    {"name": "onyx", "description": "Deep male voice"},
                    {"name": "nova", "description": "Female voice"},
                    {"name": "shimmer", "description": "Soft female voice"}
                ]
            },
            "languages": ["Auto", "Chinese", "English", "Japanese", "Korean", "German", "French", "Spanish", "Russian", "Italian", "Portuguese", "Dutch", "Polish", "Turkish", "Arabic", "Hindi", "Indonesian", "Vietnamese", "Thai", "Malay", "Swedish", "Norwegian", "Danish", "Finnish", "Greek", "Hebrew", "Burmese", "Khmer", "Lao", "Swahili", "Tagalog"],
            "logging": {"level": "INFO", "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
        }
        return AppConfig(**default_config)
    
    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)
    
    return AppConfig(**config_data)


config = load_config()