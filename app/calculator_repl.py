from app.calculator import Calculator
from app.exceptions import CalculatorError, ValidationError
from app.input_validators import validate_input, validate_operation


VALID_OPERATIONS = {
    "add",
    "subtract",
    "multiply",
    "divide",
    "power",
    "root",
    "modulus",
}


HELP_TEXT = """
Available operations:
  add <a> <b>
  subtract <a> <b>
  multiply <a> <b>
  divide <a> <b>
  power <a> <b>
  root <a> <b>
  modulus <a> <b>
Available commands:
  help     Show this help menu
  history  Show calculation history
  clear    Clear calculation history
  undo     Undo the last history change
  redo     Redo the last undone change
  save     Save history to CSV
  load     Load history from CSV
  exit     Exit the calculator
"""


class CalculatorREPL:
    """Command-line interface for the calculator."""

    def __init__(self, calculator=None):
        self.calculator = calculator or Calculator()

    def show_help(self) -> None:
        """Display available operations and commands."""
        print(HELP_TEXT)

    def show_history(self) -> None:
        """Display calculation history."""
        history = self.calculator.get_history()

        if history.empty:
            print("No calculation history.")
            return

        print(history.to_string(index=False))

    def handle_command(self, user_input: str) -> bool:
        """Handle one line of user input.

        Returns False when the user wants to exit.
        """
        user_input = user_input.strip()

        if not user_input:
            print("Please enter a command.")
            return True

        parts = user_input.split()
        command = parts[0].lower()

        if command == "exit":
            print("Goodbye!")
            return False

        if command == "help":
            self.show_help()
            return True

        if command == "history":
            self.show_history()
            return True

        if command == "clear":
            self.calculator.clear_history()
            print("History cleared.")
            return True

        if command == "undo":
            if self.calculator.undo():
                print("Undo successful.")
            else:
                print("Nothing to undo.")
            return True

        if command == "redo":
            if self.calculator.redo():
                print("Redo successful.")
            else:
                print("Nothing to redo.")
            return True

        if command == "save":
            self.calculator.save_history()
            print("History saved.")
            return True

        if command == "load":
            self.calculator.load_history()
            print("History loaded.")
            return True

        try:
            operation, a, b = validate_input(parts)
            operation = validate_operation(
                operation,
                VALID_OPERATIONS
            )

            result = self.calculator.calculate(
                operation,
                a,
                b
            )

            print(f"Result: {result}")

        except (ValidationError, CalculatorError) as exc:
            print(f"Error: {exc}")

        return True

    def run(self) -> None:
        """Start the calculator REPL."""
        print("Enhanced Calculator")
        print("Type 'help' to see available commands.")

        running = True

        while running:
            try:
                user_input = input(">>> ")
                running = self.handle_command(user_input)

            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break


def main():
    """Run the calculator application."""
    repl = CalculatorREPL()
    repl.run()


if __name__ == "__main__": # pragma: no cover
    main()