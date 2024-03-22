"""Tests our SlomanLogger class."""

from logging import DEBUG

from slomanlogger import SlomanLogger


class TestSlomanLogger:
    """Tests for our logger."""

    @staticmethod
    def test_simple_create() -> None:
        """Tests creating a logger with no input."""
        logger = SlomanLogger("logger", DEBUG)
        logger.info("Info")
        logger.debug("Debug")
        logger.warning("Warning")
        logger.critical("Critical")
        assert logger.level == DEBUG

    @staticmethod
    def test_create_with_level() -> None:
        """Tests creating a logger with a specified level."""
        logger = SlomanLogger("logger", level=DEBUG)
        logger.info("Info")
        logger.debug("Debug")
        logger.warning("Warning")
        logger.critical("Critical")
        assert logger.level == DEBUG