
"""Configuration management for RAG System."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class AppConfig(BaseModel):
    """Application configuration."""
    name: str = "RAG System"
    version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False


class ChromaDBConfig(BaseModel):
    """ChromaDB configuration."""
    persist_directory: str = "./data/chromadb"
    collection_name: str = "documents"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    distance_metric: str = "cosine"


class LLMConfig(BaseModel):
    """LLM configuration."""
    model_type: str = "llama-cpp"
    model_path: str = "./models/llama-3-8b-instruct.Q4_K_M.gguf"
    context_length: int = 4096
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.95
    n_gpu_layers: int = 35
    n_batch: int = 512
    n_threads: int = 8


class TextProcessingConfig(BaseModel):
    """Text processing configuration."""
    chunk_size: int = 512
    chunk_overlap: int = 100
    separators: list = ["\n\n", "\n", ". ", " ", ""]


class RAGConfig(BaseModel):
    """RAG configuration."""
    retrieval_k: int = 5
    relevance_threshold: float = 0.5


class ScrapingConfig(BaseModel):
    """Web scraping configuration."""
    timeout: int = 30
    max_depth: int = 3
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    log_file: str = "./logs/rag_system.log"
    max_file_size: str = "10MB"
    backup_count: int = 5


class Settings(BaseSettings):
    """Main settings class."""
    app: AppConfig = AppConfig()
    chromadb: ChromaDBConfig = ChromaDBConfig()
    llm: LLMConfig = LLMConfig()
    text_processing: TextProcessingConfig = TextProcessingConfig()
    rag: RAGConfig = RAGConfig()
    scraping: ScrapingConfig = ScrapingConfig()
    logging: LoggingConfig = LoggingConfig()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_config(config_path: str = "config.yaml") -> Settings:
    """Load configuration from YAML file."""
    config_file = Path(config_path)
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        return Settings(
            app=AppConfig(**config_data.get('app', {})),
            chromadb=ChromaDBConfig(**config_data.get('chromadb', {})),
            llm=LLMConfig(**config_data.get('llm', {})),
            text_processing=TextProcessingConfig(**config_data.get('text_processing', {})),
            rag=RAGConfig(**config_data.get('rag', {})),
            scraping=ScrapingConfig(**config_data.get('scraping', {})),
            logging=LoggingConfig(**config_data.get('logging', {}))
        )
    
    return Settings()


# Global settings instance
settings = load_config()
