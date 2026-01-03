from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    REDIS_HOST: str
    REDIS_PORT : str
    model_config = SettingsConfigDict(env_file= str(BASE_DIR / ".env"), extra="ignore")


config = Settings()
