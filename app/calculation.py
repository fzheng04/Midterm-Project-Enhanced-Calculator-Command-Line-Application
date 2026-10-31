from app.operations import OperationFactory
from datetime import datetime, timezone
from app.logger import Logger
class Calculation:
    """Represents one calculator operation and its result."""

    def __init__(self, operation: str, a: float, b: float, timestamp=None):
        self.operation = operation
        self.a = a
        self.b = b
        self.result = None
        self.timestamp = timestamp or datetime.now(
            timezone.utc
        ).isoformat(timespec="seconds")

    def execute(self) -> float:
        """Create the requested operation strategy and execute it."""
        strategy = OperationFactory.create_operation(self.operation)
        self.result = strategy.execute(self.a, self.b)
        return self.result

    def to_dict(self) -> dict:
        
        return {
            "operation": self.operation,
            "a": self.a,
            "b": self.b,
            "result": self.result,
            "timestamp": self.timestamp,
        }