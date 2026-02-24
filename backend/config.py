from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path
import os

# Resolve absolute path to the ml/models directory relative to this file
_BACKEND_DIR = Path(__file__).resolve().parent
_ML_MODELS_DIR = _BACKEND_DIR.parent / "ml" / "models"


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./returnguard.db"
    salt_secret: str = "returnguard-secret-salt-2024"
    model_path: str = str(_ML_MODELS_DIR / "fraud_model.pkl")
    feature_names_path: str = str(_ML_MODELS_DIR / "feature_names.json")
    app_env: str = "development"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
