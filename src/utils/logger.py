"""
Logging configuration and utilities.
"""
import os
import sys
from loguru import logger
from src.config.settings import logging_settings


def setup_logging():
    """Configure logging for the application."""
    
    # Remove default logger
    logger.remove()
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(logging_settings.file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Add console logging
    logger.add(
        sys.stdout,
        level=logging_settings.level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # Add file logging
    logger.add(
        logging_settings.file_path,
        level=logging_settings.level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    logger.info("Logging configured successfully")


# Initialize logging when module is imported
setup_logging()
