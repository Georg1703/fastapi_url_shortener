from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    PROJECT_NAME: str = "URL Shortner"

    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore"
    )


settings = Settings()