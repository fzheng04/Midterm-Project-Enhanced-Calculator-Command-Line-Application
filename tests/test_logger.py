
import logging

from app.logger import Logger


def test_logger_reconfiguration(tmp_path):
    logger = logging.getLogger("app.calculator")

    # Add a handler that our Logger class should preserve.
    other_handler = logging.NullHandler()
    logger.addHandler(other_handler)

    try:
        # Configure once to create a file handler.
        Logger.configure(tmp_path / "first.log")

        # Configure again to replace the existing file handler.
        Logger.configure(tmp_path / "second.log")

        # Only one managed file handler should remain.
        file_handlers = [
            handler
            for handler in logger.handlers
            if getattr(handler, "_calculator_file_handler", False)
        ]

        assert len(file_handlers) == 1

        # The unrelated handler should remain untouched.
        assert other_handler in logger.handlers

        # Verify logging works after reconfiguration.
        logger.info("Logger reconfiguration test")

        content = (tmp_path / "second.log").read_text(
            encoding="utf-8"
        )

        assert "Logger reconfiguration test" in content

    finally:
        logger.removeHandler(other_handler)
