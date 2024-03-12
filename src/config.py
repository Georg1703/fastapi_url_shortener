from typing import Literal
from functools import cached_property
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field, PostgresDsn

PROJECT_DIR = Path(__file__).parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "URL Shortner"
    ENVIRONMENT: Literal["DEV", "PYTEST"] = "DEV"

    # POSTGRESQL DEFAULT DATABASE
    DEFAULT_DATABASE_HOSTNAME: str
    DEFAULT_DATABASE_USER: str
    DEFAULT_DATABASE_PASSWORD: str
    DEFAULT_DATABASE_DB: str

    # POSTGRESQL TEST DATABASE
    TEST_DATABASE_HOSTNAME: str
    TEST_DATABASE_USER: str
    TEST_DATABASE_PASSWORD: str
    TEST_DATABASE_DB: str

    @computed_field
    @cached_property
    def DEFAULT_SQLALCHEMY_DATABASE_URI(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.DEFAULT_DATABASE_USER,
                password=self.DEFAULT_DATABASE_PASSWORD,
                host=self.DEFAULT_DATABASE_HOSTNAME,
                path=self.DEFAULT_DATABASE_DB,
            )
        )

    @computed_field
    @cached_property
    def TEST_SQLALCHEMY_DATABASE_URI(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.TEST_DATABASE_USER,
                password=self.TEST_DATABASE_PASSWORD,
                host=self.TEST_DATABASE_HOSTNAME,
                path=self.TEST_DATABASE_DB,
            )
        )

    model_config = SettingsConfigDict(
        env_file=f"{PROJECT_DIR}/.env", case_sensitive=True, extra="ignore"
    )

settings = Settings()