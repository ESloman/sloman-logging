"""Tests our SlomanLogger class."""

from logging import DEBUG, INFO
from pathlib import Path

import pytest

from slomanlogger import LEVEL_TRACE, LEVEL_VERBOSE, SlomanLogger


class TestSlomanLogger:
    """Tests for our logger."""

    @staticmethod
    def test_simple_create() -> None:
        """Tests creating a logger with no input."""
        logger = SlomanLogger("logger")
        logger.info("Info")
        logger.debug("Debug")
        logger.warning("Warning")
        logger.critical("Critical")
        logger.verbose("Verbose")
        logger.trace("Trace")
        assert logger.level == INFO

    @staticmethod
    def test_create_with_level() -> None:
        """Tests creating a logger with a specified level."""
        logger = SlomanLogger("levellogger", level=DEBUG)
        logger.info("Info")
        logger.debug("Debug")
        logger.warning("Warning")
        logger.critical("Critical")
        assert logger.level == DEBUG

    @staticmethod
    def test_create_with_path() -> None:
        """Tests creating a logger with a path."""
        logger = SlomanLogger("pathlogger", output_file=Path("output.log"))
        logger.info("Outputted to file")

    @staticmethod
    def test_adding_trace_verbose() -> None:
        """Tests trying to add trace/verbose again."""
        logger = SlomanLogger("logger")
        for name, level in [("VERBOSE", LEVEL_VERBOSE), ("TRACE", LEVEL_TRACE)]:
            with pytest.raises(AttributeError):
                logger.add_logging_level(name, level)
