import os
import logging


def setup_logger(log_dir: str = "./logs") -> logging.Logger:
    """
    Configure and return the root logger with separate handlers.
    """
    # Ensure logs directory exists
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all levels

    formatter = logging.Formatter(
        fmt="%(asctime)s || %(levelname)s || %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handlers
    debug_handler = logging.FileHandler(os.path.join(log_dir, "debug.log"))
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)

    info_handler = logging.FileHandler(os.path.join(log_dir, "info.log"))
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    error_handler = logging.FileHandler(os.path.join(log_dir, "error.log"))
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Clear existing handlers to avoid duplication in reloads (e.g., uvicorn)
    if logger.handlers:
        logger.handlers.clear()

    # Add handlers
    logger.addHandler(debug_handler)
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    return logger
