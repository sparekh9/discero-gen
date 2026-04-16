"""Environment-backed settings loader."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    tavily_api_key: str = ""

    discero_model: str = "gpt-4o-2024-08-06"
    discero_mini_model: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


def load_settings() -> Settings:
    return Settings()
