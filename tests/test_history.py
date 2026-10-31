import pandas as pd

from app.calculation import Calculation
from app.history import HistoryManager

import pytest
from app.exceptions import HistoryError
def make_calculation(operation, a, b):
    """Create and execute a calculation for history tests."""
    calculation = Calculation(operation, a, b)
    calculation.execute()
    return calculation


def test_history_starts_empty():
    history = HistoryManager()

    assert history.is_empty()
    assert len(history) == 0
    assert list(history.data.columns) == [
        "operation",
        "a",
        "b",
        "result",
        "timestamp",
    ]


def test_add_calculation_to_history():
    history = HistoryManager()
    calculation = make_calculation("add", 5, 3)

    history.add(calculation)

    assert len(history) == 1
    assert not history.is_empty()

    row = history.data.iloc[0]

    assert row["operation"] == "add"
    assert row["a"] == 5
    assert row["b"] == 3
    assert row["result"] == 8


def test_clear_history():
    history = HistoryManager()
    history.add(make_calculation("multiply", 4, 5))

    history.clear()

    assert history.is_empty()
    assert len(history) == 0


def test_data_returns_copy():
    history = HistoryManager()
    history.add(make_calculation("add", 1, 2))

    copied_history = history.data
    copied_history.loc[0, "result"] = 999

    assert history.data.loc[0, "result"] == 3


def test_save_and_load_history(tmp_path):
    file_path = tmp_path / "history.csv"

    history = HistoryManager()
    history.add(make_calculation("add", 5, 3))
    history.add(make_calculation("multiply", 4, 5))

    history.save(str(file_path))

    assert file_path.exists()

    loaded_history = HistoryManager()
    loaded_history.load(str(file_path))

    assert len(loaded_history) == 2
    assert loaded_history.data.iloc[0]["operation"] == "add"
    assert loaded_history.data.iloc[0]["result"] == 8
    assert loaded_history.data.iloc[1]["operation"] == "multiply"
    assert loaded_history.data.iloc[1]["result"] == 20


def test_save_creates_parent_directory(tmp_path):
    file_path = tmp_path / "data" / "calculator" / "history.csv"

    history = HistoryManager()
    history.add(make_calculation("subtract", 10, 4))

    history.save(str(file_path))

    assert file_path.exists()
    assert file_path.parent.exists()


def test_save_file_without_parent_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    history = HistoryManager()
    history.add(make_calculation("add", 2, 2))

    history.save("history.csv")

    assert (tmp_path / "history.csv").exists()


def test_load_missing_file_clears_history(tmp_path):
    history = HistoryManager()
    history.add(make_calculation("power", 2, 3))

    missing_file = tmp_path / "does_not_exist.csv"

    history.load(str(missing_file))

    assert history.is_empty()


def test_replace_history():
    history = HistoryManager()

    replacement = pd.DataFrame(
        [
            {
                "operation": "divide",
                "a": 20,
                "b": 4,
                "result": 5,
            }
        ]
    )

    history.replace(replacement)

    assert len(history) == 1
    assert history.data.iloc[0]["operation"] == "divide"
    assert history.data.iloc[0]["result"] == 5


def test_replace_uses_copy():
    history = HistoryManager()

    replacement = pd.DataFrame(
        [
            {
                "operation": "add",
                "a": 1,
                "b": 1,
                "result": 2,
            }
        ]
    )

    history.replace(replacement)

    replacement.loc[0, "result"] = 100

    assert history.data.loc[0, "result"] == 2

def test_history_includes_timestamp(tmp_path):
    history = HistoryManager()
    history.add(make_calculation("add", 5, 3))

    file_path = tmp_path / "history.csv"
    history.save(str(file_path))

    saved_data = pd.read_csv(file_path)

    assert "timestamp" in saved_data.columns
    assert pd.notna(saved_data.iloc[0]["timestamp"])

    loaded = HistoryManager()
    loaded.load(str(file_path))

    assert len(loaded) == 1
    assert loaded.data.iloc[0]["result"] == 8
    assert loaded.data.iloc[0]["timestamp"]


def test_load_legacy_history(tmp_path):
    """Older CSV files without timestamps must still load."""
    file_path = tmp_path / "old_history.csv"

    pd.DataFrame([
        {
            "operation": "add",
            "a": 2,
            "b": 3,
            "result": 5,
        }
    ]).to_csv(file_path, index=False)

    history = HistoryManager()
    history.load(str(file_path))

    assert len(history) == 1
    assert history.data.iloc[0]["result"] == 5
    assert isinstance(history.data.iloc[0]["timestamp"], str)


@pytest.mark.parametrize(
    "csv_content",
    [
        "operation,a,b\nadd,2,3\n",
        "operation,a,b,result\nadd,hello,3,5\n",
        "operation,a,b,result\nunknown,2,3,5\n",
        (
            "operation,a,b,result,timestamp\n"
            "add,2,3,5,invalid-date\n"
        ),
    ],
)
def test_malformed_csv_preserves_history(tmp_path, csv_content):
    history = HistoryManager()
    history.add(make_calculation("add", 5, 3))

    file_path = tmp_path / "malformed.csv"
    file_path.write_text(csv_content, encoding="utf-8")

    with pytest.raises(HistoryError, match="Failed to load history"):
        history.load(str(file_path))

    # An invalid file must not destroy the previous history.
    assert len(history) == 1
    assert history.data.iloc[0]["result"] == 8


def test_custom_csv_encoding(tmp_path):
    file_path = tmp_path / "history_utf16.csv"

    history = HistoryManager(encoding="utf-16")
    history.add(make_calculation("multiply", 4, 5))
    history.save(str(file_path))

    loaded = HistoryManager(encoding="utf-16")
    loaded.load(str(file_path))

    assert len(loaded) == 1
    assert loaded.data.iloc[0]["result"] == 20

def test_save_failure(tmp_path, monkeypatch):
    history = HistoryManager()
    history.add(make_calculation("add", 2, 3))

    def fail_write(self, *args, **kwargs):
        raise OSError("Disk full")

    monkeypatch.setattr(pd.DataFrame, "to_csv", fail_write)

    with pytest.raises(
        HistoryError,
        match="Failed to save history"
    ):
        history.save(str(tmp_path / "history.csv"))


@pytest.mark.parametrize(
    "csv_content",
    [
        "operation,a,b,result\n,2,3,5\n",
        "operation,a,b,result\nadd,inf,3,5\n",
        "operation,a,b,result\nadd,2,3,nan\n",
        (
            "operation,a,b,result,timestamp\n"
            "add,2,3,5,\n"
        ),
    ],
)
def test_additional_invalid_csv(tmp_path, csv_content):
    file_path = tmp_path / "invalid.csv"
    file_path.write_text(csv_content, encoding="utf-8")

    history = HistoryManager()

    with pytest.raises(
        HistoryError,
        match="Failed to load history"
    ):
        history.load(str(file_path))
