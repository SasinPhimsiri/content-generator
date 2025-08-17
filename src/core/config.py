"""Configuration management for Jenosize Content Generator."""

import os
from pathlib import Path
from typing import Dict, List, Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class OllamaConfig(BaseSettings):
    """Ollama configuration."""
    base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    model: str = Field(default="llama3.1:8b", env="OLLAMA_MODEL")


class APIConfig(BaseSettings):
    """API configuration."""
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    workers: int = Field(default=4, env="API_WORKERS")


class RAGConfig(BaseSettings):
    """RAG configuration."""
    # Removed ChromaDB - using simple_db only
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 512
    chunk_overlap: int = 50
    similarity_threshold: float = 0.7
    max_retrieved_chunks: int = 5


class ContentConfig(BaseSettings):
    """Content generation configuration."""
    max_content_length: int = Field(default=2000, env="MAX_CONTENT_LENGTH")
    temperature: float = Field(default=0.7, env="TEMPERATURE")
    top_p: float = Field(default=0.9, env="TOP_P")


# Rate limiting removed - not needed for prototype


class Config:
    """Main configuration class."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._load_config()
        
        # Initialize sub-configurations
        self.ollama = OllamaConfig()
        self.api = APIConfig()
        self.rag = RAGConfig()
        self.content = ContentConfig()
    
    def _load_config(self):
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.yaml_config = yaml.safe_load(f)
    
    @property
    def agents(self) -> Dict[str, Any]:
        """Get agent configurations."""
        return self.yaml_config.get("agents", {})
    
    @property
    def content_categories(self) -> List[str]:
        """Get content categories."""
        return self.yaml_config.get("content_generation", {}).get("categories", [])
    
    @property
    def industries(self) -> List[str]:
        """Get industries."""
        return self.yaml_config.get("content_generation", {}).get("industries", [])
    
    @property
    def workflow_steps(self) -> List[str]:
        """Get workflow steps."""
        return self.yaml_config.get("content_generation", {}).get("workflow", [])


# Global configuration instance
config = Config()
