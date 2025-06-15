import logging
import os
from datetime import datetime


def setup_logger(name, log_file=None, level=logging.INFO):
    """Set up logger with the specified name and log file."""
    # Create logs directory if it doesn't exist
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create file handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Create a default logger
default_logger = setup_logger(
    'sudoku_ocr',
    os.path.join('logs', f'sudoku_ocr_{datetime.now().strftime("%Y%m%d")}.log')
)
