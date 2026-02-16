"""
config file - 

using pydantic to validate environment variables 
ensures type safety and provides defaults for missing variables. This centralizes configuration management and makes it easier to maintain and debug the application.

"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    application settings loaded from environment variables or .env file
    - database_url: Connection string for the database (default: sqlite)
    - redis_url: Connection string for Redis (default: redis://localhost:6379)
    - ollama_host: URL for Ollama API (default: http://localhost:11434)
    - chroma_persist_dir: Directory for ChromaDB storage (default: ./data
    - app_name: Name of the application (default: Caseflow Chat)
    - debug: Enable debug mode (default: True)

    these are called when the application starts and can be accessed throughout the codebase via the `settings` instance
    this is backup and fallback for environment variables, allowing for easy configuration without hardcoding values in the codebase
    this does not set the environment variables themselves, but rather provides a structured way to access them with defaults and validation
    """
    
    # Database
    database_url: str = Field(
        default="sqlite:///./data/caseflow.db",
        description="Database connection string"
    )
    
    # Redis (Job Queue)
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection for job queue"
    )
    
    # Ollama
    ollama_host: str = Field(
        default="http://localhost:11434",
        description="Ollama API endpoint"
    )
    
    # ChromaDB
    chroma_persist_dir: str = Field(
        default="./data/chroma_data",
        description="ChromaDB storage directory"
    )
    
    # Application
    app_name: str = "Caseflow Chat"
    debug: bool = True
    
    class Config:
        # This tells Pydantic to read from .env file
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create a global settings instance
# This is imported everywhere we need config
settings = Settings()