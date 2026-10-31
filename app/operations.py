from abc import ABC, abstractmethod
from app.exceptions import OperationError

class Operation(ABC):
    """Base class for calculator operations."""

    @abstractmethod
    def execute(self, a: float, b: float) -> float:
        pass  # pragma: no cover


class Addition(Operation):
    def execute(self, a: float, b: float) -> float:
        return a + b


class Subtraction(Operation):
    def execute(self, a: float, b: float) -> float:
        return a - b


class Multiplication(Operation):
    def execute(self, a: float, b: float) -> float:
        return a * b


class Division(Operation):
    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError("Division by zero is not allowed.")
        return a / b

class Modulus(Operation):
    """Return the remainder of a division."""

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError("Modulus by zero is not allowed.")

        return a % b
class IntegerDivision(Operation):
    """Perform integer division."""

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError(
                "Integer division by zero is not allowed."
            )
        return a // b
class Percentage(Operation):
    """Calculate a as a percentage of b."""

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError(
                "Percentage division by zero is not allowed."
            )

        return (a / b) * 100
class Power(Operation):
    def execute(self, a: float, b: float) -> float:
        return a ** b


class Root(Operation):
    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError("Root degree cannot be zero.")

        if a < 0 and int(b) % 2 == 0:
            raise OperationError(
    "Even root of a negative number is not allowed."
    )

        if a < 0:
            return -((-a) ** (1 / b))

        return a ** (1 / b)


class OperationFactory:
    """Factory for creating operation objects."""

    _operations = {
        "add": Addition,
        "subtract": Subtraction,
        "multiply": Multiplication,
        "divide": Division,
        "power": Power,
        "root": Root,
        "modulus": Modulus,
        "int_divide": IntegerDivision,
        "percent": Percentage,
    }

    @classmethod
    def create_operation(cls, operation_name: str) -> Operation:
        operation_class = cls._operations.get(operation_name.lower())

        if operation_class is None:
            raise OperationError(f"Invalid operation: {operation_name}")

        return operation_class()

