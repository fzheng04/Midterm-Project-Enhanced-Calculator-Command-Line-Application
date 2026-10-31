class CalculatorError(Exception):
    """Base exception for calculator errors."""


class ValidationError(CalculatorError):
    """Raised when user input is invalid."""


class OperationError(CalculatorError):
    """Raised when a calculation cannot be performed."""


class ConfigurationError(CalculatorError):
    """Raised when calculator configuration is invalid."""

class HistoryError(CalculatorError):
    """Raised when calculation history cannot be saved or loaded."""