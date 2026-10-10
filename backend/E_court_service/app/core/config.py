from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ecourts_api_key: str
    ecourts_base_url: str
    database_url: str
    auth_service_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
