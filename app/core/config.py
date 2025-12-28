"""Application configuration settings."""
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
    )
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./students_grades.db"
    
    # API
    api_title: str = "Students Grades API"
    api_version: str = "1.0.0"


settings = Settings()

