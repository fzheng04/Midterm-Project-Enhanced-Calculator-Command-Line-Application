import logging

import pandas as pd

from app.calculator import Calculator
import pytest

class DummyConfig:
    """Simple configuration object for calculator tests."""

    def __init__(
        self,
        history_file,
        max_history=100,
        auto_save=False,
        precision=4,
        max_input_value=1000000,
    ):
        self.history_file = str(history_file)
        self.max_history = max_history
        self.auto_save = auto_save
        self.precision = precision
        self.max_input_value = max_input_value

class RecordingObserver:
    """Observer used to verify notifications during tests."""

    def __init__(self):
        self.calculations = []

    def update(self, calculator, calculation):
        self.calculations.append(calculation)


def make_calculator(
    tmp_path,
    max_history=100,
    auto_save=False,
):
    config = DummyConfig(
        tmp_path / "history.csv",
        max_history=max_history,
        auto_save=auto_save,
    )

    return Calculator(config)


def test_calculate_returns_result_and_adds_history(tmp_path):
    calculator = make_calculator(tmp_path)

    result = calculator.calculate("add", 5, 3)

    assert result == 8
    assert len(calculator.get_history()) == 1
    assert calculator.get_history().iloc[0]["operation"] == "add"
    assert calculator.get_history().iloc[0]["result"] == 8


def test_calculator_loads_existing_history(tmp_path):
    history_file = tmp_path / "history.csv"

    existing = pd.DataFrame(
        [
            {
                "operation": "multiply",
                "a": 4,
                "b": 5,
                "result": 20,
            }
        ]
    )

    existing.to_csv(history_file, index=False)

    config = DummyConfig(history_file)
    calculator = Calculator(config)

    assert len(calculator.get_history()) == 1
    assert calculator.get_history().iloc[0]["result"] == 20


def test_clear_history(tmp_path):
    calculator = make_calculator(tmp_path)

    calculator.calculate("add", 1, 2)
    calculator.clear_history()

    assert calculator.get_history().empty


def test_clear_empty_history(tmp_path):
    calculator = make_calculator(tmp_path)

    calculator.clear_history()

    assert calculator.get_history().empty


def test_undo_and_redo(tmp_path):
    calculator = make_calculator(tmp_path)

    calculator.calculate("add", 5, 3)

    assert calculator.undo() is True
    assert calculator.get_history().empty

    assert calculator.redo() is True
    assert len(calculator.get_history()) == 1
    assert calculator.get_history().iloc[0]["result"] == 8


def test_undo_when_nothing_to_undo(tmp_path):
    calculator = make_calculator(tmp_path)

    assert calculator.undo() is False


def test_redo_when_nothing_to_redo(tmp_path):
    calculator = make_calculator(tmp_path)

    assert calculator.redo() is False


def test_clear_can_be_undone(tmp_path):
    calculator = make_calculator(tmp_path)

    calculator.calculate("multiply", 6, 7)
    calculator.clear_history()

    assert calculator.get_history().empty

    calculator.undo()

    assert len(calculator.get_history()) == 1
    assert calculator.get_history().iloc[0]["result"] == 42


def test_save_history(tmp_path):
    calculator = make_calculator(tmp_path)
    custom_file = tmp_path / "saved.csv"

    calculator.calculate("subtract", 10, 3)
    calculator.save_history(str(custom_file))

    assert custom_file.exists()


def test_save_history_uses_config_path(tmp_path):
    calculator = make_calculator(tmp_path)

    calculator.calculate("add", 2, 2)
    calculator.save_history()

    assert (tmp_path / "history.csv").exists()


def test_load_history(tmp_path):
    calculator = make_calculator(tmp_path)

    load_file = tmp_path / "load.csv"

    pd.DataFrame(
        [
            {
                "operation": "power",
                "a": 2,
                "b": 3,
                "result": 8,
            }
        ]
    ).to_csv(load_file, index=False)

    calculator.load_history(str(load_file))

    assert len(calculator.get_history()) == 1
    assert calculator.get_history().iloc[0]["operation"] == "power"


def test_load_history_uses_config_path(tmp_path):
    history_file = tmp_path / "history.csv"

    pd.DataFrame(
        [
            {
                "operation": "root",
                "a": 16,
                "b": 2,
                "result": 4,
            }
        ]
    ).to_csv(history_file, index=False)

    config = DummyConfig(history_file)
    calculator = Calculator(config)

    calculator.clear_history()
    calculator.load_history()

    assert len(calculator.get_history()) == 1
    assert calculator.get_history().iloc[0]["result"] == 4


def test_history_limit(tmp_path):
    calculator = make_calculator(
        tmp_path,
        max_history=2,
    )

    calculator.calculate("add", 1, 1)
    calculator.calculate("add", 2, 2)
    calculator.calculate("add", 3, 3)

    history = calculator.get_history()

    assert len(history) == 2
    assert history.iloc[0]["result"] == 4
    assert history.iloc[1]["result"] == 6


def test_add_and_remove_observer(tmp_path):
    calculator = make_calculator(tmp_path)
    observer = RecordingObserver()

    calculator.add_observer(observer)
    calculator.calculate("add", 5, 5)

    assert len(observer.calculations) == 1
    assert observer.calculations[0].result == 10

    calculator.remove_observer(observer)
    calculator.calculate("add", 2, 2)

    assert len(observer.calculations) == 1


def test_remove_unregistered_observer(tmp_path):
    calculator = make_calculator(tmp_path)
    observer = RecordingObserver()

    calculator.remove_observer(observer)

    assert observer not in calculator._observers


def test_auto_save_enabled(tmp_path):
    calculator = make_calculator(
        tmp_path,
        auto_save=True,
    )

    calculator.calculate("multiply", 4, 5)

    history_file = tmp_path / "history.csv"

    assert history_file.exists()


def test_auto_save_disabled(tmp_path):
    calculator = make_calculator(
        tmp_path,
        auto_save=False,
    )

    calculator.calculate("multiply", 4, 5)

    history_file = tmp_path / "history.csv"

    assert not history_file.exists()


def test_logging_observer(tmp_path, caplog):
    calculator = make_calculator(tmp_path)

    with caplog.at_level(logging.INFO):
        calculator.calculate("add", 2, 3)

    assert "add 2 3 = 5" in caplog.text


def test_clear_history_autosaves(tmp_path):
    calculator = make_calculator(tmp_path, auto_save=True)

    calculator.calculate("add", 5, 3)
    calculator.clear_history()

    # Restart the calculator and reload its saved history
    restarted = make_calculator(tmp_path, auto_save=True)

    assert restarted.get_history().empty


@pytest.mark.parametrize(
    ("action", "expected_rows"),
    [
        ("undo", 0),
        ("redo", 1),
    ],
)
def test_undo_redo_autosaves(tmp_path, action, expected_rows):
    calculator = make_calculator(tmp_path, auto_save=True)
    calculator.calculate("add", 5, 3)

    if action == "redo":
        assert calculator.undo() is True
        # Save the starting state so redo is tested independently.
        calculator.save_history()

    assert getattr(calculator, action)() is True

    restarted = make_calculator(tmp_path, auto_save=True)

    assert len(restarted.get_history()) == expected_rows

from app.exceptions import ValidationError


def test_calculation_precision(tmp_path):
    calculator = make_calculator(tmp_path)

    result = calculator.calculate("divide", 10, 3)

    assert result == 3.3333
    assert calculator.get_history().iloc[0]["result"] == 3.3333


def test_input_exceeds_maximum(tmp_path):
    calculator = make_calculator(tmp_path)

    with pytest.raises(ValidationError, match="exceeds maximum"):
        calculator.calculate("add", 1000001, 5)


def test_input_at_maximum(tmp_path):
    calculator = make_calculator(tmp_path)

    assert calculator.calculate("subtract", 1000000, 1) == 999999


@pytest.mark.parametrize("value", [float("inf"), float("nan")])
def test_non_finite_inputs(tmp_path, value):
    calculator = make_calculator(tmp_path)

    with pytest.raises(ValidationError, match="finite"):
        calculator.calculate("add", value, 5)