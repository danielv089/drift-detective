import logging

def get_logger(name, log_filepath: str) -> logging.Logger:
    """
    Get a logger instance that logs to both console and a log file.
    """

    logger=logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:

        file_handler=logging.FileHandler(log_filepath, mode='a')
        console_handler=logging.StreamHandler()

        formatter=logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
