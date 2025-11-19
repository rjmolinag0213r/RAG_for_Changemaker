
"""Logging configuration for RAG System."""

import sys
from pathlib import Path
from loguru import logger
from backend.config import settings


def setup_logger():
    """Configure the logger with file and console outputs."""
    # Remove default handler
    logger.remove()
    
    # Create logs directory if it doesn't exist
    log_path = Path(settings.logging.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Add console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.logging.level,
        colorize=True
    )
    
    # Add file handler with rotation
    logger.add(
        settings.logging.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.logging.level,
        rotation=settings.logging.max_file_size,
        retention=settings.logging.backup_count,
        compression="zip"
    )
    
    return logger


# Initialize logger
log = setup_logger()
