"""
App settings module.

This uses Pydantic's BaseSettings + SettingsConfigDict to automatically:
- Load variables from a .env file (for local dev)
- Override with actual environment vars (in production)
- Validate and type-check them (e.g. PostgresDsn)
- Cache the settings (so theyre not reloaded on every call)

TL;DR: no more os.getenv() or load_dotenv() crap.
Just define fields here, and access via `settings.SOME_VAR`.
"""

from functools import lru_cache

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    For local development, create a .env file in project root.
    For production, set these as actual environment variables.
    """

    # Pydantic settings model config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra env vars
    )

    # App settings
    APP_NAME: str = "FastAPI Experiment"
    DEBUG: bool = False

    # Database setings
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_dev",
        description="Async PostgreSQL connection string",
    )

    # Database connection pool settings
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False  # Set True to log SQL queries


@lru_cache
def get_settings() -> Settings:
    """
    Cache settings so we dont re-read environment on every call.
    Dependency injection pattern for FastAPI
    """
    return Settings()


# Convenience instance for importing
settings = get_settings()
