from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    openai_api_key: str
    openai_realtime_model: str = "gpt-4o-realtime-preview-2024-12-17"
    openai_realtime_url: str = "wss://api.openai.com/v1/realtime"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @computed_field
    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def openai_realtime_ws_url(self) -> str:
        return f"{self.openai_realtime_url}?model={self.openai_realtime_model}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
