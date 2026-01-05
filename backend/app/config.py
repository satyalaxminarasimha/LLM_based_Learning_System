from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI-Powered Learning System"
    api_prefix: str = "/api"
    db_url: str = "sqlite:///./data.db"
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    openai_api_key: str | None = None
    ai_model: str = "gpt-4o-mini"
    frontend_origin: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
