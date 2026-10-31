
# Midterm Project: Enhanced Calculator Command-Line Application

## Project Description

This project is an enhanced command-line calculator built with Python using object-oriented programming principles. It supports ten arithmetic operations, calculation history, undo/redo, logging, CSV data persistence, and configurable settings through environment variables.

The application uses the Factory, Memento, and Observer design patterns. It also includes error handling, input validation, automated testing with pytest, and continuous integration through GitHub Actions.

This project builds upon Assignment 5 by introducing additional arithmetic operations, improved configuration management, timestamped history, file logging, and color-coded terminal output.

## Features

- Ten arithmetic operations
- Interactive command-line interface (REPL)
- Calculation history with undo/redo
- Automatic and manual history saving using pandas
- CSV history with timestamps
- File logging using Python's logging module
- Configuration management using python-dotenv
- Input validation and custom exceptions
- Configurable calculation precision and maximum input values
- Color-coded terminal output using Colorama
- 100% test coverage using pytest and pytest-cov
- Automated testing through GitHub Actions

## Project Structure

```text
project_root/
├── app/
│   ├── __init__.py
│   ├── calculator.py
│   ├── calculation.py
│   ├── calculator_config.py
│   ├── calculator_memento.py
│   ├── calculator_repl.py
│   ├── exceptions.py
│   ├── history.py
│   ├── input_validators.py
│   ├── operations.py
│   └── logger.py
├── tests/
├── .github/
│   └── workflows/
│       └── python-app.yml
├── .env.example
├── requirements.txt
├── main.py
└── README.md
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/fzheng04/Midterm-Project-Enhanced-Calculator-Command-Line-Application.git

cd Midterm-Project-Enhanced-Calculator-Command-Line-Application
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file using the provided example:

```bash
cp .env.example .env
```

Example configuration:

```env
CALCULATOR_LOG_DIR=logs
CALCULATOR_LOG_FILE=logs/calculator.log
CALCULATOR_HISTORY_DIR=data
CALCULATOR_HISTORY_FILE=data/history.csv
CALCULATOR_MAX_HISTORY_SIZE=100
CALCULATOR_AUTO_SAVE=true
CALCULATOR_PRECISION=4
CALCULATOR_MAX_INPUT_VALUE=1000000
CALCULATOR_DEFAULT_ENCODING=utf-8
```

These settings control logging, history management, numerical precision, input limits, and file encoding. Default values are used when settings are not provided.

## Running the Application

Start the calculator:

```bash
python3 main.py
```

Enter commands using the following format:

```text
operation number1 number2
```

### Supported Arithmetic Operations

| Command | Description | Example | Result |
|---|---|---|---|
| add | Addition | add 10 5 | 15.0 |
| subtract | Subtraction | subtract 10 5 | 5.0 |
| multiply | Multiplication | multiply 10 5 | 50.0 |
| divide | Division | divide 10 4 | 2.5 |
| power | Exponentiation | power 2 3 | 8.0 |
| root | Nth root | root 81 2 | 9.0 |
| modulus | Remainder | modulus 10 3 | 1.0 |
| int_divide | Floor division | int_divide 10 3 | 3.0 |
| percent | Percentage (a / b) * 100 | percent 25 100 | 25.0 |
| abs_diff | Absolute difference | abs_diff 3 10 | 7.0 |

Integer division uses Python's `//` operator, which rounds down toward negative infinity.

### Additional Commands

| Command | Description |
|---|---|
| history | Display calculation history |
| clear | Clear calculation history |
| undo | Undo the previous history change |
| redo | Redo an undone history change |
| save | Save calculation history to CSV |
| load | Load calculation history from CSV |
| help | Display available commands |
| exit | Exit the application |

### Example Session

```text
>>> add 10 5
Result: 15.0

>>> percent 25 100
Result: 25.0

>>> undo
Undo successful.

>>> redo
Redo successful.

>>> save
History saved.

>>> exit
Goodbye!
```

## Design Patterns

### Factory Pattern

The OperationFactory class creates the appropriate arithmetic operation based on the user's command. This allows new operations to be added without significantly changing the existing calculator logic.

### Memento Pattern

The Memento pattern manages calculator history states and provides undo and redo functionality.

### Observer Pattern

The calculator uses observers to respond automatically to new calculations.

- LoggingObserver records calculation details.
- AutoSaveObserver saves calculation history to CSV when automatic saving is enabled.

These patterns help separate responsibilities and make the application easier to maintain and extend.

## History Management

Calculation history is managed using pandas DataFrames.

Each calculation contains the following information:

- Operation
- First operand
- Second operand
- Result
- Timestamp

History can be saved to and loaded from CSV files. The application validates loaded data and provides error messages when files are missing or malformed. Older CSV files without timestamps are also supported.

## Logging and Error Handling

The application uses Python's logging module to record important events.

Logging levels include:

- INFO: Successful calculations and application events
- WARNING: Invalid inputs and validation problems
- ERROR: Failed calculations and other errors

Logs are written to the configured log file.

Custom exceptions handle invalid operations, division by zero, invalid numerical inputs, configuration errors, and history persistence failures.

## Optional Advanced Feature

### Color-Coded Output

Colorama is used to improve the command-line interface.

- Green: Successful calculations
- Red: Error messages
- Yellow: Warnings
- Cyan: Help information

This makes the application easier to read and improves the user experience.

## Unit Testing

The application uses pytest for automated unit testing.

Tests cover:

- Arithmetic operations and edge cases
- Operation Factory functionality
- Calculation history
- Undo and redo
- Observer notifications
- Configuration validation
- Logging
- CSV saving and loading
- Input validation
- REPL commands and error handling

Run all tests:

```bash
python3 -m pytest -v
```

Run tests with coverage:

```bash
python3 -m pytest --cov=app --cov-branch --cov-report=term-missing --cov-fail-under=100
```

Generate an HTML coverage report:

```bash
python3 -m pytest --cov=app --cov-branch --cov-report=html
```

The project achieves 100% test coverage, exceeding the required 90% threshold.

## Continuous Integration

GitHub Actions automatically executes the test suite whenever code is pushed to the main branch or a pull request is opened.

The workflow performs the following tasks:

1. Checks out the repository
2. Sets up Python
3. Installs dependencies
4. Runs pytest
5. Measures test coverage
6. Fails the workflow if the required coverage threshold is not met

The workflow is defined in:

```text
.github/workflows/python-app.yml
```

Test results can be viewed in the Actions tab on GitHub.

## Technologies Used

- Python 3.13
- pytest
- pytest-cov
- pandas
- python-dotenv
- Colorama
- Git and GitHub
- GitHub Actions

## Conclusion

This project demonstrates object-oriented programming, software design patterns, automated testing, file persistence, logging, and continuous integration.

By extending the previous calculator application, the midterm incorporates additional functionality while maintaining a modular and testable codebase.
