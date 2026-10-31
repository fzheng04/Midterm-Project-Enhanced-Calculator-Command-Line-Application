
import logging
from pathlib import Path


class Logger:
    """Configure file logging for the calculator."""

    @staticmethod
    def configure(log_file, encoding="utf-8"):
        """Write calculator events to a configured log file."""

        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger("app.calculator")
        logger.setLevel(logging.INFO)

        # Replace only file handlers managed by this class.
        # Preserve other handlers, including pytest's log capture.
        for handler in logger.handlers[:]:
            if getattr(handler, "_calculator_file_handler", False):
                logger.removeHandler(handler)
                handler.close()

        file_handler = logging.FileHandler(
            path,
            encoding=encoding,
        )
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        file_handler._calculator_file_handler = True

        logger.addHandler(file_handler)

        return logger
