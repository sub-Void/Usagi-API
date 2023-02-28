import logging
import sys
from pathlib import Path

from loguru import logger
from loguru._logger import Logger

from .config import LoggingConfig

# Reference: gucharbon - https://github.com/tiangolo/fastapi/issues/2019

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logger(
    level: str,
    format: str,
    filepath: Path | None = None, 
    rotation: str | None = None, 
    retention: str | None = None, 
    backtrace: bool | None = None, 
    diagnose: bool | None = None, 
) -> Logger:
    """Define the global logger to be used by your entire service.
    Arguments:
        level: the minimum log-level to log.
        format: the logformat to use.
        filepath: the path where to store the logfiles.
        rotation: when to rotate the logfile.
        retention: when to remove logfiles.
    Returns:
        the logger to be used by the service.
    References:
        - [Loguru: Intercepting logging logs #247](https://github.com/Delgan/loguru/issues/247)
        - [Gunicorn: generic logging options #1572](https://github.com/benoitc/gunicorn/issues/1572#issuecomment-638391953)
    """

    # Remove loguru default logger
    logger.remove()
    # Cath all existing loggers
    LOGGERS = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    # Add stdout logger
    logger.add(
        sys.stdout,
        enqueue=True,
        colorize=True,
        backtrace=backtrace,
        level=level.upper(),
        format=format,
        diagnose=diagnose,
    )
    # Optionally add filepath logger
    if filepath:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(filepath),
            rotation=rotation,
            retention=retention,
            enqueue=True,
            colorize=False,
            backtrace=True,
            level=level.upper(),
            format=format,
        )
    # Overwrite config of standard library root logger
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    # Overwrite handlers of all existing loggers from standard library logging
    for _logger in LOGGERS:
        _logger.handlers = [InterceptHandler()]
        _logger.propagate = False

    return logger


def setup_logger_from_config(settings: LoggingConfig | None = None) -> Logger:
    """Define the global logger to be used by your entire service.
    Arguments:
        settings: the logging settings to apply.
    Returns:
        the logger instance.
    """
    
    # Parse from env when no settings are given
    if not settings:
        settings = LoggingConfig()
    # Return logger even though it's not necessary
    return setup_logger(
        settings.level,
        settings.format,
        settings.filepath,
        settings.rotation,
        settings.retention,
        settings.backtrace,
        settings.diagnose,
    )