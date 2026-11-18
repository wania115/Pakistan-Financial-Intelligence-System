from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Pakistan Financial Intelligence System"
    debug: bool = False
    database_url: str = "sqlite:///./pfis.db"

    model_config = SettingsConfigDict(
        env_prefix="PFIS_",
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
