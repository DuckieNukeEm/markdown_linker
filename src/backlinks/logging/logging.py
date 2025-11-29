import logging


def setup_logging(log_level, log_file=None):
    """Setup logging configuration"""
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    handlers = []

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(levelname)s: %(message)s")
    )
    handlers.append(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        )
        handlers.append(file_handler)

    logging.basicConfig(
        level=level_map.get(log_level.upper(), logging.INFO),
        handlers=handlers,
        force=True,
    )
