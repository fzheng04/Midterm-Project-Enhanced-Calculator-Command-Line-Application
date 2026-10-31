
import codecs
import math
import os
from pathlib import Path

from dotenv import load_dotenv

from app.exceptions import ConfigurationError


class CalculatorConfig:
    """Load and validate calculator settings."""

    def __init__(self):
        load_dotenv()

        # File and directory settings
        self.log_dir = os.getenv(
            "CALCULATOR_LOG_DIR", "logs"
        )
        self.history_dir = os.getenv(
            "CALCULATOR_HISTORY_DIR", "data"
        )

        self.log_file = os.getenv(
            "CALCULATOR_LOG_FILE"
        ) or str(Path(self.log_dir) / "calculator.log")

        self.history_file = os.getenv(
            "CALCULATOR_HISTORY_FILE"
        ) or str(Path(self.history_dir) / "history.csv")

        # History settings
        self.max_history = self._load_max_history()

        self.auto_save = self._load_boolean(
            os.getenv("CALCULATOR_AUTO_SAVE", "true")
        )

        # Calculation settings
        self.precision = self._load_integer(
            "CALCULATOR_PRECISION", 4, minimum=0
        )

        self.max_input_value = self._load_positive_float(
            "CALCULATOR_MAX_INPUT_VALUE", 1000000
        )

        # Encoding settings
        self.default_encoding = os.getenv(
            "CALCULATOR_DEFAULT_ENCODING", "utf-8"
        ).strip()

        try:
            codecs.lookup(self.default_encoding)
        except LookupError as exc:
            raise ConfigurationError(
                "CALCULATOR_DEFAULT_ENCODING is invalid."
            ) from exc

    def _load_max_history(self) -> int:
        """Load the maximum history size."""

        # Support the older Module 5 variable.
        name = "CALCULATOR_MAX_HISTORY_SIZE"

        if os.getenv(name) is None:
            name = "CALCULATOR_MAX_HISTORY"

        return self._load_integer(name, 100, minimum=1)

    @staticmethod
    def _load_integer(name, default, minimum):
        """Load and validate an integer configuration."""

        value = os.getenv(name, str(default))

        try:
            number = int(value)
        except ValueError as exc:
            raise ConfigurationError(
                f"{name} must be an integer."
            ) from exc

        if number < minimum:
            if minimum == 1:
                message = "must be greater than zero."
            else:
                message = f"must be at least {minimum}."

            raise ConfigurationError(
                f"{name} {message}"
            )

        return number

    @staticmethod
    def _load_positive_float(name, default):
        """Load and validate a positive numerical setting."""

        value = os.getenv(name, str(default))

        try:
            number = float(value)
        except ValueError as exc:
            raise ConfigurationError(
                f"{name} must be a number."
            ) from exc

        if not math.isfinite(number) or number <= 0:
            raise ConfigurationError(
                f"{name} must be a positive finite number."
            )

        return number

    @staticmethod
    def _load_boolean(value: str) -> bool:
        """Convert supported text values into booleans."""

        value = value.strip().lower()

        if value in {"true", "1", "yes", "on"}:
            return True

        if value in {"false", "0", "no", "off"}:
            return False

        raise ConfigurationError(
            f"Invalid boolean configuration value: {value}"
        )
