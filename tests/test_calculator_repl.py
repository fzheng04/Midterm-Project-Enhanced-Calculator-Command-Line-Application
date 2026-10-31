
import pandas as pd
import pytest

from app.calculator_repl import CalculatorREPL, HELP_TEXT
from app.exceptions import OperationError
from colorama import Fore
from app.exceptions import HistoryError
class StubCalculator:
    """Simple calculator stub used for REPL tests."""

    def __init__(self):
        self.history = pd.DataFrame(
            columns=["operation", "a", "b", "result"]
        )
        self.undo_result = False
        self.redo_result = False
        self.saved = False
        self.loaded = False
        self.cleared = False

    def calculate(self, operation, a, b):
        if operation == "divide" and b == 0:
            raise OperationError(
                "Division by zero is not allowed."
            )

        if operation == "modulus" and b == 0:
            raise OperationError(
                "Modulus by zero is not allowed."
            )

        if operation == "int_divide" and b == 0:
            raise OperationError(
                "Integer division by zero is not allowed."
            )

        if operation == "percent" and b == 0:
            raise OperationError(
                "Percentage division by zero is not allowed."
            )

        # Use lambdas so only the requested operation executes.
        results = {
            "add": lambda: a + b,
            "subtract": lambda: a - b,
            "multiply": lambda: a * b,
            "divide": lambda: a / b,
            "power": lambda: a ** b,
            "root": lambda: a ** (1 / b),
            "modulus": lambda: a % b,
            "int_divide": lambda: a // b,
            "percent": lambda: (a / b) * 100,
            "abs_diff": lambda: abs(a - b),
        }

        if operation not in results:
            raise OperationError(
                f"Invalid operation: {operation}"
            )

        result = results[operation]()

        new_row = pd.DataFrame(
            [
                {
                    "operation": operation,
                    "a": a,
                    "b": b,
                    "result": result,
                }
            ]
        )

        self.history = pd.concat(
            [self.history, new_row],
            ignore_index=True,
        )

        return result

    def get_history(self):
        return self.history.copy()

    def clear_history(self):
        self.history = self.history.iloc[0:0]
        self.cleared = True

    def undo(self):
        return self.undo_result

    def redo(self):
        return self.redo_result

    def save_history(self):
        self.saved = True

    def load_history(self):
        self.loaded = True


def test_repl_uses_provided_calculator():
    calculator = StubCalculator()
    repl = CalculatorREPL(calculator)

    assert repl.calculator is calculator


def test_show_help(capsys):
    repl = CalculatorREPL(StubCalculator())

    repl.show_help()

    output = capsys.readouterr().out

    assert "Available operations:" in output
    assert "Available commands:" in output
    assert HELP_TEXT.strip() in output


def test_show_empty_history(capsys):
    repl = CalculatorREPL(StubCalculator())

    repl.show_history()

    output = capsys.readouterr().out

    assert "No calculation history." in output


def test_show_history(capsys):
    calculator = StubCalculator()
    calculator.calculate("add", 5, 3)

    repl = CalculatorREPL(calculator)
    repl.show_history()

    output = capsys.readouterr().out

    assert "add" in output
    assert "8" in output


def test_empty_command(capsys):
    repl = CalculatorREPL(StubCalculator())

    result = repl.handle_command("   ")

    assert result is True
    assert "Please enter a command." in capsys.readouterr().out


def test_exit_command(capsys):
    repl = CalculatorREPL(StubCalculator())

    result = repl.handle_command("exit")

    assert result is False
    assert "Goodbye!" in capsys.readouterr().out


def test_help_command(capsys):
    repl = CalculatorREPL(StubCalculator())

    assert repl.handle_command("help") is True

    assert "Available operations:" in capsys.readouterr().out


def test_history_command(capsys):
    repl = CalculatorREPL(StubCalculator())

    assert repl.handle_command("history") is True

    assert "No calculation history." in capsys.readouterr().out


def test_clear_command(capsys):
    calculator = StubCalculator()
    repl = CalculatorREPL(calculator)

    assert repl.handle_command("clear") is True

    assert calculator.cleared is True
    assert "History cleared." in capsys.readouterr().out


def test_undo_success(capsys):
    calculator = StubCalculator()
    calculator.undo_result = True

    repl = CalculatorREPL(calculator)

    assert repl.handle_command("undo") is True
    assert "Undo successful." in capsys.readouterr().out


def test_undo_failure(capsys):
    calculator = StubCalculator()
    calculator.undo_result = False

    repl = CalculatorREPL(calculator)

    assert repl.handle_command("undo") is True
    assert "Nothing to undo." in capsys.readouterr().out


def test_redo_success(capsys):
    calculator = StubCalculator()
    calculator.redo_result = True

    repl = CalculatorREPL(calculator)

    assert repl.handle_command("redo") is True
    assert "Redo successful." in capsys.readouterr().out


def test_redo_failure(capsys):
    calculator = StubCalculator()
    calculator.redo_result = False

    repl = CalculatorREPL(calculator)

    assert repl.handle_command("redo") is True
    assert "Nothing to redo." in capsys.readouterr().out


def test_save_command(capsys):
    calculator = StubCalculator()
    repl = CalculatorREPL(calculator)

    assert repl.handle_command("save") is True
    assert calculator.saved is True
    assert "History saved." in capsys.readouterr().out


def test_load_command(capsys):
    calculator = StubCalculator()
    repl = CalculatorREPL(calculator)

    assert repl.handle_command("load") is True
    assert calculator.loaded is True
    assert "History loaded." in capsys.readouterr().out


@pytest.mark.parametrize(
    "command,expected",
    [
        ("add 5 3", 8.0),
        ("subtract 9 4", 5.0),
        ("multiply 6 7", 42.0),
        ("divide 10 2", 5.0),
        ("power 2 3", 8.0),
        ("root 81 2", 9.0),
        ("modulus 10 3", 1.0),
        ("int_divide 10 3", 3.0),
        ("int_divide 20 4", 5.0),
        ("percent 25 100", 25.0),
        ("percent 50 200", 25.0),
        ("percent 75 150", 50.0),
        ("abs_diff 10 3", 7.0),
        ("abs_diff 3 10", 7.0),
        ("abs_diff -5 3", 8.0),
        ("abs_diff 5 5", 0.0),
        
    ],
)
def test_valid_calculations(command, expected, capsys):
    repl = CalculatorREPL(StubCalculator())

    assert repl.handle_command(command) is True

    output = capsys.readouterr().out

    assert f"Result: {expected}" in output


def test_invalid_operation(capsys):
    repl = CalculatorREPL(StubCalculator())

    assert repl.handle_command("unknown_operation 10 3") is True

    output = capsys.readouterr().out

    assert "Error: Invalid operation: unknown_operation" in output


def test_invalid_number(capsys):
    repl = CalculatorREPL(StubCalculator())

    assert repl.handle_command("add hello 3") is True

    output = capsys.readouterr().out

    assert "Error:" in output
    assert "hello" in output


def test_wrong_number_of_arguments(capsys):
    repl = CalculatorREPL(StubCalculator())

    assert repl.handle_command("add 5") is True

    output = capsys.readouterr().out

    assert "Error:" in output


def test_calculator_error(capsys):
    repl = CalculatorREPL(StubCalculator())

    assert repl.handle_command("divide 10 0") is True

    output = capsys.readouterr().out

    assert "Division by zero is not allowed." in output


def test_percentage_by_zero_repl(capsys):
    repl = CalculatorREPL(StubCalculator())

    assert repl.handle_command("percent 25 0") is True

    output = capsys.readouterr().out

    assert "Percentage division by zero" in output


def test_run_until_exit(monkeypatch, capsys):
    repl = CalculatorREPL(StubCalculator())

    commands = iter(["add 2 3", "exit"])

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(commands),
    )

    repl.run()

    output = capsys.readouterr().out

    assert "Enhanced Calculator" in output
    assert "Result: 5.0" in output
    assert "Goodbye!" in output


def test_run_handles_eof(monkeypatch, capsys):
    repl = CalculatorREPL(StubCalculator())

    def raise_eof(_):
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)

    repl.run()

    assert "Goodbye!" in capsys.readouterr().out


def test_run_handles_keyboard_interrupt(monkeypatch, capsys):
    repl = CalculatorREPL(StubCalculator())

    def raise_interrupt(_):
        raise KeyboardInterrupt

    monkeypatch.setattr(
        "builtins.input",
        raise_interrupt,
    )

    repl.run()

    assert "Goodbye!" in capsys.readouterr().out


def test_main(monkeypatch):
    called = {"run": False}

    def fake_run(self):
        called["run"] = True

    monkeypatch.setattr(
        "app.calculator_repl.CalculatorREPL.run",
        fake_run,
    )

    from app.calculator_repl import main

    main()

    assert called["run"] is True

def test_success_output_is_green(capsys):
    repl = CalculatorREPL(StubCalculator())

    repl.handle_command("add 2 3")

    output = capsys.readouterr().out

    assert f"{Fore.GREEN}Result: 5.0" in output


def test_error_output_is_red(capsys):
    repl = CalculatorREPL(StubCalculator())

    repl.handle_command("add hello 3")

    output = capsys.readouterr().out

    assert f"{Fore.RED}Error:" in output


def test_warning_output_is_yellow(capsys):
    repl = CalculatorREPL(StubCalculator())

    repl.handle_command("")

    output = capsys.readouterr().out

    assert (
        f"{Fore.YELLOW}Please enter a command."
        in output
    )


def test_save_command_error(monkeypatch, capsys):
    calculator = StubCalculator()

    def fail_save():
        raise HistoryError("Unable to save history")

    monkeypatch.setattr(calculator, "save_history", fail_save)

    repl = CalculatorREPL(calculator)

    assert repl.handle_command("save") is True

    output = capsys.readouterr().out

    assert "Error: Unable to save history" in output


def test_load_command_error(monkeypatch, capsys):
    calculator = StubCalculator()

    def fail_load():
        raise HistoryError("Unable to load history")

    monkeypatch.setattr(calculator, "load_history", fail_load)

    repl = CalculatorREPL(calculator)

    assert repl.handle_command("load") is True

    output = capsys.readouterr().out

    assert "Error: Unable to load history" in output