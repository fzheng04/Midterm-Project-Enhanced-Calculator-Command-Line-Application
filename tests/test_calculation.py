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

    assert calculation.to_dict() == {
        "operation": "add",
        "a": 2,
        "b": 3,
        "result": 5,
    }


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