import pytest

from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigurationError


def test_default_configuration(monkeypatch):
    monkeypatch.delenv("CALCULATOR_HISTORY_FILE", raising=False)
    monkeypatch.delenv("CALCULATOR_MAX_HISTORY", raising=False)
    monkeypatch.delenv("CALCULATOR_AUTO_SAVE", raising=False)

    config = CalculatorConfig()

    assert config.history_file == "data/history.csv"
    assert config.max_history == 100
    assert config.auto_save is True


def test_environment_configuration(monkeypatch):
    monkeypatch.setenv(
        "CALCULATOR_HISTORY_FILE",
        "custom/history.csv"
    )
    monkeypatch.setenv(
        "CALCULATOR_MAX_HISTORY",
        "250"
    )
    monkeypatch.setenv(
        "CALCULATOR_AUTO_SAVE",
        "false"
    )

    config = CalculatorConfig()

    assert config.history_file == "custom/history.csv"
    assert config.max_history == 250
    assert config.auto_save is False


@pytest.mark.parametrize(
    "value",
    ["true", "1", "yes", "on", "TRUE", " Yes "],
)
def test_true_boolean_values(value):
    assert CalculatorConfig._load_boolean(value) is True


@pytest.mark.parametrize(
    "value",
    ["false", "0", "no", "off", "FALSE", " Off "],
)
def test_false_boolean_values(value):
    assert CalculatorConfig._load_boolean(value) is False


def test_invalid_max_history_type(monkeypatch):
    monkeypatch.setenv(
        "CALCULATOR_MAX_HISTORY",
        "abc"
    )

    with pytest.raises(
        ConfigurationError,
        match="CALCULATOR_MAX_HISTORY must be an integer."
    ):
        CalculatorConfig()


@pytest.mark.parametrize(
    "value",
    ["0", "-1", "-100"],
)
def test_invalid_max_history_value(monkeypatch, value):
    monkeypatch.setenv(
        "CALCULATOR_MAX_HISTORY",
        value
    )

    with pytest.raises(
        ConfigurationError,
        match="CALCULATOR_MAX_HISTORY must be greater than zero."
    ):
        CalculatorConfig()


def test_invalid_boolean_value():
    with pytest.raises(
        ConfigurationError,
        match="Invalid boolean configuration value: maybe"
    ):
        CalculatorConfig._load_boolean("maybe")


def test_new_configuration_settings(monkeypatch):
    monkeypatch.setenv("CALCULATOR_LOG_DIR", "custom_logs")
    monkeypatch.setenv(
        "CALCULATOR_LOG_FILE", "custom_logs/test.log"
    )
    monkeypatch.setenv(
        "CALCULATOR_HISTORY_DIR", "custom_data"
    )
    monkeypatch.delenv(
        "CALCULATOR_HISTORY_FILE", raising=False
    )
    monkeypatch.setenv(
        "CALCULATOR_MAX_HISTORY_SIZE", "200"
    )
    monkeypatch.setenv("CALCULATOR_PRECISION", "6")
    monkeypatch.setenv(
        "CALCULATOR_MAX_INPUT_VALUE", "5000"
    )
    monkeypatch.setenv(
        "CALCULATOR_DEFAULT_ENCODING", "utf-8"
    )

    config = CalculatorConfig()

    assert config.log_dir == "custom_logs"
    assert config.log_file == "custom_logs/test.log"
    assert config.history_dir == "custom_data"
    assert config.history_file == "custom_data/history.csv"
    assert config.max_history == 200
    assert config.precision == 6
    assert config.max_input_value == 5000
    assert config.default_encoding == "utf-8"


@pytest.mark.parametrize(
    "setting,value",
    [
        ("CALCULATOR_MAX_HISTORY_SIZE", "abc"),
        ("CALCULATOR_MAX_HISTORY_SIZE", "-5"),
        ("CALCULATOR_PRECISION", "invalid"),
        ("CALCULATOR_PRECISION", "-1"),
        ("CALCULATOR_MAX_INPUT_VALUE", "-100"),
        ("CALCULATOR_MAX_INPUT_VALUE", "hello"),
        ("CALCULATOR_MAX_INPUT_VALUE", "nan"),
        ("CALCULATOR_DEFAULT_ENCODING", "not-an-encoding"),
    ],
)
def test_invalid_new_configuration(monkeypatch, setting, value):
    monkeypatch.setenv(setting, value)

    with pytest.raises(ConfigurationError):
        CalculatorConfig()
