"""
Simple file + console logger used across the app so that technical
errors never leak to the user as raw tracebacks.
"""
import logging
from config.settings import settings

_logger = None


def get_logger() -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    logger = logging.getLogger("interview_prep_bot")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_handler = logging.FileHandler(settings.LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        )
        logger.addHandler(file_handler)

    _logger = logger
    return _logger


def log_error(context: str, exc: Exception) -> None:
    get_logger().error("%s: %s", context, repr(exc))


def log_info(message: str) -> None:
    get_logger().info(message)
