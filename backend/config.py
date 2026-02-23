from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./returnguard.db"
    salt_secret: str = "returnguard-secret-salt-2024"
    model_path: str = "../ml/models/fraud_model.pkl"
    feature_names_path: str = "../ml/models/feature_names.json"
    app_env: str = "development"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
