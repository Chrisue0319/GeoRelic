from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./lbs_poi.db"
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    RATE_LIMIT_PER_MINUTE: int = 60
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
