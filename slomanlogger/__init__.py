"""Module for SlomanLogger class.

Acts as a wrapper for logging.Logger - handles a lot of the normal setup configuration.

Example:

.. code-block:: python

    logger = SlomanLogger("my_logger")
    logger.info("Created a new logger")
    logger.debug("Debug message")
    logger.error("Something went wrong!")

"""

__version__ = "0.1.0-beta.2"

import logging
import sys
from logging import FileHandler, LogRecord
from pathlib import Path
from typing import ClassVar

LEVEL_TRACE: int = 5
LEVEL_VERBOSE: int = 15


class SlomanLogger:
    """Sloman Logger that wraps logging.Logger configuration and functionality.

    Default logger is setup to output to standard out with some formatting.
    The SlomanLogger class implements a singleton pattern for it's instance and logger object -
    provided you use the same logger name.

    .. code-block:: python

        logger1 = SlomanLogger("my_logger")
        logger2 = SlomanLogger("my_logger")
        logger3 = SlomanLogger("another_logger")

        # true
        logger1 is logger2

        # false
        logger1 is logger3

    """

    _instance: "SlomanLogger" = None
    _logger: logging.Logger = None

    def __new__(cls, *args: tuple[any], **_: dict[str, any]) -> "SlomanLogger":
        """Ensures we only create one instance of this class for each logger name."""
        if cls._instance is None or (cls._instance.logger is not None and cls._instance.logger.name != args[0]):
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, name: str, level: int = logging.INFO, output_file: Path | None = None) -> None:
        """Initialises the class and creates the new logger based on name and level.

        Args:
            name (str): the logger's name
            level (int, optional): the logging level for this logger. Defaults to logging.INFO.
            output_file (Path, optional): the output file for this logger. Defaults to None.
        """
        if not self._logger:
            # set additional logging levels
            if not hasattr(logging, "VERBOSE"):
                self.add_logging_level("VERBOSE", LEVEL_VERBOSE)
            if not hasattr(logging, "TRACE"):
                self.add_logging_level("TRACE", LEVEL_TRACE)
            self._logger = self._setup_logger(name, level, output_file)
        self.name = name

    @property
    def logger(self) -> logging.Logger:
        """The actual logging.Logger object."""
        return self._logger

    @property
    def level(self) -> int:
        """Returns the logger level."""
        return self._logger.level

    @staticmethod
    def _setup_logger(name: str, level: int, output_file: Path | None = None) -> logging.Logger:
        """Sets up the logger with some standard formatting.

        Should only be called internally.

        Args:
            name (str): name of the logger
            level (int): the logger's Level
            output_file (Path): the output file. Defaults to None.

        Returns:
            logging.Logger: the newly created Logger
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        formatting = "[%(asctime)s] [%(levelname)s] %(funcName)s: %(message)s"
        colour_formatter = _ColourFormatter(formatting)
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setFormatter(colour_formatter)
        logger.addHandler(stream_handler)

        if output_file:
            # add basic file handler
            file_handler = FileHandler(output_file, "w", "utf-8")
            formatter = logging.Formatter(formatting)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    @staticmethod
    def add_logging_level(name: str, num: int, method_name: str | None = None) -> None:
        """Comprehensively adds a new logging level to the `logging` module.

        Args:
            name (str): becomes an attribute of the `logging` module with the value
            num (int): becomes a convenience method for both `logging` itself and the
                class returned by `logging.getLoggerClass()` (usually just `logging.Logger`).
            method_name (str): the name of the method to set. If not specified, `name.lower()` is
                used.

        To avoid accidental clobberings of existing attributes, this method will
        raise an `AttributeError` if the level name is already an attribute of the
        `logging` module or if the method name is already present.

        Example:
        -------
        >>> SlomanLogger.add_logging_level('TRACE', logging.DEBUG - 5)
        >>> logging.getLogger(__name__).setLevel("TRACE")
        >>> logging.getLogger(__name__).trace('that worked')
        >>> logging.trace('so did this')
        >>> logging.TRACE
        5

        """
        if not method_name:
            method_name = name.lower()

        if hasattr(logging, name):
            msg = f"{name} already defined in logging module."
            raise AttributeError(msg)
        if hasattr(logging, method_name):
            msg = f"{method_name} already defined in logging module."
            raise AttributeError(msg)
        if hasattr(logging.getLoggerClass(), method_name):
            msg = f"{method_name} already defined in logger class."
            raise AttributeError(msg)

        # This method was inspired by the answers to Stack Overflow post
        # http://stackoverflow.com/q/2183233/2988730, especially
        # http://stackoverflow.com/a/13638084/2988730
        def log_for_level(self: "logging.Logger", message: str, *args: tuple[any], **kwargs: dict[str, any]) -> None:
            """Log for level wrapper."""
            if self.isEnabledFor(num):
                self._log(num, message, args, **kwargs)

        def log_to_root(message: str, *args: tuple[any], **kwargs: dict[str, any]) -> None:
            """Log to root wrapper."""
            logging.log(num, message, *args, **kwargs)

        logging.addLevelName(num, name)
        setattr(logging, name, num)
        setattr(logging.getLoggerClass(), method_name, log_for_level)
        setattr(logging, method_name, log_to_root)

    def info(self, message: str, *args: tuple[any], **kwargs: dict[str, any]) -> None:
        """logging.Logger.info wrapper.

        Args:
            message (str): the message to log
        """
        self.logger.info(message, *args, stacklevel=2, **kwargs)

    def trace(self, message: str, *args: tuple[any], **kwargs: dict[str, any]) -> None:
        """logging.Logger.trace wrapper.

        Args:
            message (str): the message to log
        """
        self.logger.trace(message, *args, stacklevel=3, **kwargs)

    def verbose(self, message: str, *args: tuple[any], **kwargs: dict[str, any]) -> None:
        """logging.Logger.verbose wrapper.

        Args:
            message (str): the message to log
        """
        self.logger.verbose(message, *args, stacklevel=3, **kwargs)

    def debug(self, message: str, *args: tuple[any], **kwargs: dict[str, any]) -> None:
        """logging.Logger.debug wrapper.

        Args:
            message (str): the message to log
        """
        self.logger.debug(message, *args, stacklevel=2, **kwargs)

    def warning(self, message: str, *args: tuple[any], **kwargs: dict[str, any]) -> None:
        """logging.Logger.warning wrapper.

        Args:
            message (str): the message to log
        """
        self.logger.warning(message, *args, stacklevel=2, **kwargs)

    def error(self, message: str, *args: tuple[any], **kwargs: dict[str, any]) -> None:
        """logging.Logger.error wrapper.

        Args:
            message (str): the message to log
        """
        self.logger.error(message, *args, stacklevel=2, **kwargs)

    def exception(self, message: str, *args: tuple[any], **kwargs: dict[str, any]) -> None:
        """logging.Logger.exception wrapper.

        Args:
            message (str): the message to log
        """
        self.logger.exception(message, *args, stacklevel=2, **kwargs)

    def critical(self, message: str, *args: tuple[any], **kwargs: dict[str, any]) -> None:
        """logging.Logger.critical wrapper.

        Args:
            message (str): the message to log
        """
        self.logger.critical(message, *args, stacklevel=2, **kwargs)


class _ColourFormatter(logging.Formatter):
    """Colour Formatter.

    # ANSI codes are a bit weird to decipher if you're unfamiliar with them, so here's a refresher
    # It starts off with a format like \x1b[XXXm where XXX is a semicolon separated list of commands
    # The important ones here relate to colour.
    # 30-37 are black, red, green, yellow, blue, magenta, cyan and white in that order
    # 40-47 are the same except for the background
    # 90-97 are the same but "bright" foreground
    # 100-107 are the same as the bright ones but for the background.
    # 1 means bold, 2 means dim, 0 means reset, and 4 means underline.
    """

    LEVEL_COLOURS: ClassVar = [
        (logging.DEBUG, "\x1b[32;1m"),
        (logging.INFO, "\x1b[34;1m"),
        (logging.WARNING, "\x1b[33;1m"),
        (logging.ERROR, "\x1b[31m"),
        (logging.CRITICAL, "\x1b[41m"),
        (LEVEL_VERBOSE, "\x1b[36;1m"),
        (LEVEL_TRACE, "\x1b[31;1m"),
    ]

    FORMATS: ClassVar = {
        level: logging.Formatter(
            f"\x1b[30;1m[%(asctime)s]\x1b[0m {colour}[%(levelname)s] \x1b[0m\x1b[35m%(funcName)8s:\x1b[0m %(message)s",
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self: "_ColourFormatter", record: LogRecord) -> str:
        """Formats the message appropriately with colour.

        Args:
            record (LogRecord): the record to colour

        Returns:
            str: the formatted text
        """
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f"\x1b[31m{text}\x1b[0m"

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output
