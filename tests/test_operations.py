import pytest
from app.operations import Modulus
from app.exceptions import OperationError
from app.operations import IntegerDivision
from app.operations import Percentage
from app.operations import AbsoluteDifference
from app.operations import (
    Addition,
    Subtraction,
    Multiplication,
    Division,
    Power,
    Root,
    OperationFactory,
)


@pytest.mark.parametrize(
    "operation_class,a,b,expected",
    [
        (Addition, 2, 3, 5),
        (Addition, -1, 1, 0),
        (Subtraction, 5, 3, 2),
        (Multiplication, 4, 3, 12),
        (Division, 10, 2, 5),
        (Power, 2, 3, 8),
        (Root, 16, 2, 4),
        (Root, 27, 3, 3),
        (Modulus, 10, 3, 1),
        (Modulus, 20, 4, 0),
        (Modulus, 7, 2, 1),
        (IntegerDivision, 10, 3, 3),
        (IntegerDivision, 20, 4, 5),
        (IntegerDivision, -10, 3, -4),
        (Percentage, 25, 100, 25),
        (Percentage, 50, 200, 25),
        (Percentage, 75, 150, 50),
        (Percentage, 0, 100, 0),
        (AbsoluteDifference, 10, 3, 7),
        (AbsoluteDifference, 3, 10, 7),
        (AbsoluteDifference, -5, 3, 8),
        (AbsoluteDifference, 5, 5, 0),
    ],
)
def test_operations(operation_class, a, b, expected):
    operation = operation_class()
    assert operation.execute(a, b) == pytest.approx(expected)


def test_division_by_zero():
    operation = Division()

    with pytest.raises(
        OperationError,
        match="Division by zero is not allowed."
    ):
        operation.execute(10, 0)


def test_root_degree_zero():
    operation = Root()

    with pytest.raises(
        OperationError,
        match="Root degree cannot be zero."
    ):
        operation.execute(16, 0)


def test_even_root_of_negative_number():
    operation = Root()

    with pytest.raises(
        OperationError,
        match="Even root of a negative number is not allowed."
    ):
        operation.execute(-16, 2)


def test_negative_odd_root():
    operation = Root()

    assert operation.execute(-27, 3) == pytest.approx(-3)


@pytest.mark.parametrize(
    "name,expected_class",
    [
        ("add", Addition),
        ("subtract", Subtraction),
        ("multiply", Multiplication),
        ("divide", Division),
        ("power", Power),
        ("root", Root),
        ("modulus", Modulus),
        ("int_divide", IntegerDivision),
        ("percent", Percentage),
        ("abs_diff", AbsoluteDifference),
    ],
)
def test_operation_factory(name, expected_class):
    operation = OperationFactory.create_operation(name)
    assert isinstance(operation, expected_class)


def test_factory_is_case_insensitive():
    operation = OperationFactory.create_operation("ADD")
    assert isinstance(operation, Addition)

def test_invalid_operation():
    with pytest.raises(OperationError):
        OperationFactory.create_operation("unknown_operation")

def test_modulus_by_zero():
    operation = Modulus()

    with pytest.raises(OperationError, match="Modulus by zero"):
        operation.execute(10, 0)


def test_integer_division_by_zero():
    operation = IntegerDivision()

    with pytest.raises(
        OperationError,
        match="Integer division by zero is not allowed."
    ):
        operation.execute(10, 0)
def test_percentage_by_zero():
    operation = Percentage()

    with pytest.raises(
        OperationError,
        match="Percentage division by zero is not allowed."
    ):
        operation.execute(25, 0)