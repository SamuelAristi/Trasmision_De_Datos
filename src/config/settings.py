"""
Configuration settings for the database connection and application.
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    host: str = Field(default="localhost", env="PG_HOST")
    port: int = Field(default=5432, env="PG_PORT")
    name: str = Field(default="DropshipingDB", env="PG_DB")
    user: str = Field(default="postgres", env="PG_USER")
    password: str = Field(default="postgres", env="PG_PASS")
    db_schema: str = Field(default="public", env="PG_SCHEMA_RAW")
    
    @property
    def connection_string(self) -> str:
        """Generate PostgreSQL connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    
    level: str = Field(default="INFO", env="LOG_LEVEL")
    file_path: str = Field(default="logs/app.log", env="LOG_FILE")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


# Global settings instances
db_settings = DatabaseSettings()
logging_settings = LoggingSettings()
