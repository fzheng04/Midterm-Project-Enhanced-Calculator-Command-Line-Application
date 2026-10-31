import pytest

from app.calculation import Calculation
from app.exceptions import OperationError


@pytest.mark.parametrize(
    "operation,a,b,expected",
    [
        ("add", 5, 3, 8),
        ("subtract", 9, 4, 5),
        ("multiply", 6, 7, 42),
        ("divide", 12, 3, 4),
        ("power", 2, 4, 16),
        ("root", 81, 2, 9),
        ("int_divide", 10, 3, 3),
        ("int_divide", 20, 4, 5),
        ("percent", 25, 100, 25),
        ("percent", 50, 200, 25),
        ("percent", 75, 150, 50),
        ("abs_diff", 10, 3, 7),
        ("abs_diff", 3, 10, 7),
        ("abs_diff", -5, 3, 8),
    ],
)
def test_calculation_execute(operation, a, b, expected):
    calculation = Calculation(operation, a, b)

    result = calculation.execute()

    assert result == pytest.approx(expected)
    assert calculation.result == pytest.approx(expected)


def test_calculation_to_dict():
    calculation = Calculation("add", 2, 3)
    calculation.execute()

    data = calculation.to_dict()

    assert data["operation"] == "add"
    assert data["a"] == 2
    assert data["b"] == 3
    assert data["result"] == 5
    assert isinstance(data["timestamp"], str)
    assert data["timestamp"]

def test_calculation_result_starts_as_none():
    calculation = Calculation("add", 1, 2)

    assert calculation.result is None

def test_invalid_calculation_operation():
    calculation = Calculation("unknown_operation", 10, 3)

    with pytest.raises(
        OperationError,
        match="Invalid operation: unknown_operation",
    ):
        calculation.execute()