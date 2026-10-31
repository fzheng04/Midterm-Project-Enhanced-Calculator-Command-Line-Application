import logging
from abc import ABC, abstractmethod
from app.logger import Logger
from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import MementoManager
from app.history import HistoryManager
import math
from app.exceptions import ValidationError, OperationError

logger = logging.getLogger(__name__)


class CalculatorObserver(ABC):
    """Base class for calculator observers."""

    @abstractmethod
    def update(self, calculator, calculation) -> None:
        """Receive calculation notifications."""
        pass  # pragma: no cover

class LoggingObserver(CalculatorObserver):
    """Log completed calculations."""

    def update(self, calculator, calculation) -> None:
        logger.info(
            "%s %s %s = %s",
            calculation.operation,
            calculation.a,
            calculation.b,
            calculation.result,
        )


class AutoSaveObserver(CalculatorObserver):
    """Automatically save history after calculations."""

    def update(self, calculator, calculation) -> None:
        if calculator.config.auto_save:
            calculator.save_history()


class Calculator:
    """Facade that provides a simple interface to calculator features."""

    def __init__(self, config=None):
        self.config = config or CalculatorConfig()

        # Configure file logging
        Logger.configure(
            getattr(self.config, "log_file", "logs/calculator.log"),
            getattr(self.config, "default_encoding", "utf-8"),
        )

        # Initialize history and Memento Pattern
        self.history = HistoryManager(
            encoding=getattr(
                self.config,
                "default_encoding",
                "utf-8",
            )
        )
        self.mementos = MementoManager()

        # Initialize Observer Pattern
        self._observers = []
        self.add_observer(LoggingObserver())
        self.add_observer(AutoSaveObserver())

        # Load previously saved history
        self.history.load(self.config.history_file)

        logger.info("Calculator initialized")

    def add_observer(self, observer: CalculatorObserver) -> None:
        """Register an observer."""
        self._observers.append(observer)

    def remove_observer(self, observer: CalculatorObserver) -> None:
        """Remove a registered observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self, calculation: Calculation) -> None:
        """Notify observers that a calculation was completed."""
        for observer in self._observers:
            observer.update(self, calculation)

    def calculate(self, operation: str, a: float, b: float) -> float:
        """Perform a validated calculation and save it to history."""

        for value in (a, b):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValidationError("Operands must be numbers.")

            if not math.isfinite(value):
                logger.warning("Non-finite operand: %r", value)
                raise ValidationError("Inputs must be finite numbers.")

            if abs(value) > self.config.max_input_value:
                raise ValidationError(
                    f"Input exceeds maximum allowed value: "
                    f"{self.config.max_input_value}"
                )

        calculation = Calculation(operation, a, b)

        try:
            result = calculation.execute()

        except OperationError:
            logger.exception("Operation '%s' failed", operation)
            raise

        except (OverflowError, ZeroDivisionError) as exc:
            logger.exception("Operation '%s' failed", operation)
            raise OperationError(f"Calculation failed: {exc}") from exc

        if isinstance(result, complex) or not math.isfinite(result):
            raise OperationError("Calculation produced an invalid result.")

        result = round(result, self.config.precision)
        calculation.result = result

        self.mementos.save_state(self.history.data)

        self.history.add(calculation)
        self._limit_history()

        self._notify_observers(calculation)
        return result
    

    def get_history(self):
        """Return the current calculation history."""
        return self.history.data

    def clear_history(self) -> None:
        """Clear calculation history while preserving undo state."""
        if self.history.is_empty():
            return

        self.mementos.save_state(self.history.data)
        self.history.clear()

        # Automatically save the cleared history if enabled.
        if self.config.auto_save:
            self.save_history()
    def save_history(self, file_path=None) -> None:
        """Save history to CSV."""
        path = file_path or self.config.history_file
        self.history.save(path)

    def load_history(self, file_path=None) -> None:
        """Load history from CSV."""
        path = file_path or self.config.history_file

        previous_history = self.history.data
        self.history.load(path)

        self.mementos.save_state(previous_history)

    
    def undo(self) -> bool:
        """Restore the previous calculator state."""
        previous_state = self.mementos.undo(self.history.data)

        if previous_state is None:
            return False

        self.history.replace(previous_state)
        self._autosave_if_enabled()

        return True


    
    def redo(self) -> bool:
        """Restore a previously undone calculator state."""
        next_state = self.mementos.redo(self.history.data)

        if next_state is None:
            return False

        self.history.replace(next_state)
        self._autosave_if_enabled()

        return True


    def _limit_history(self) -> None:
        """Keep history within the configured maximum size."""
        if len(self.history) > self.config.max_history:
            limited_history = self.history.data.tail(
                self.config.max_history
            )
            self.history.replace(limited_history)



    def _autosave_if_enabled(self) -> None:
        """Persist history when auto-save is enabled."""
        if self.config.auto_save:
            self.save_history()
