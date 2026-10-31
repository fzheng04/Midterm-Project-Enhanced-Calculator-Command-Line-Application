
import math
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from app.calculation import Calculation
from app.exceptions import HistoryError, OperationError
from app.operations import OperationFactory


class HistoryManager:
    """Manage calculator history using pandas."""

    COLUMNS = ["operation", "a", "b", "result", "timestamp"]

    def __init__(self, encoding="utf-8"):
        self.encoding = encoding
        self._history = pd.DataFrame(columns=self.COLUMNS)

    @property
    def data(self) -> pd.DataFrame:
        """Return a copy of calculation history."""
        return self._history.copy()

    def add(self, calculation: Calculation) -> None:
        """Add a completed calculation to history."""
        new_row = pd.DataFrame([calculation.to_dict()])

        self._history = pd.concat(
            [self._history, new_row],
            ignore_index=True,
        )

    def clear(self) -> None:
        """Clear all calculation history."""
        self._history = pd.DataFrame(columns=self.COLUMNS)

    def save(self, file_path: str) -> None:
        """Save calculation history to a CSV file."""
        path = Path(file_path)

        try:
            path.parent.mkdir(parents=True, exist_ok=True)

            self._history.to_csv(
                path,
                index=False,
                encoding=self.encoding,
            )

        except (OSError, UnicodeError, ValueError) as exc:
            raise HistoryError(
                f"Failed to save history: {exc}"
            ) from exc

    def load(self, file_path: str) -> None:
        """Load and validate calculations from a CSV file."""
        path = Path(file_path)

        if not path.exists():
            self.clear()
            return

        try:
            data = pd.read_csv(
                path,
                encoding=self.encoding,
            )

            required = {"operation", "a", "b", "result"}
            missing = required - set(data.columns)

            if missing:
                raise ValueError(
                    f"Missing required columns: {sorted(missing)}"
                )

            has_timestamp = "timestamp" in data.columns
            calculations = []

            for index, row in data.iterrows():
                operation = row["operation"]

                if not isinstance(operation, str) or not operation:
                    raise ValueError(
                        f"Invalid operation in row {index + 1}"
                    )

                # Ensure the stored operation is supported.
                OperationFactory.create_operation(operation)

                a = float(row["a"])
                b = float(row["b"])
                result = float(row["result"])

                if not all(math.isfinite(v) for v in (a, b, result)):
                    raise ValueError(
                        f"Invalid numerical value in row {index + 1}"
                    )

                timestamp = None

                if has_timestamp:
                    timestamp = row["timestamp"]

                    if not isinstance(timestamp, str):
                        raise ValueError(
                            f"Missing timestamp in row {index + 1}"
                        )

                    # Validate the ISO 8601 timestamp.
                    datetime.fromisoformat(timestamp)

                # Reconstruct the Calculation instance.
                calculation = Calculation(
                    operation,
                    a,
                    b,
                    timestamp=timestamp,
                )
                calculation.result = result

                calculations.append(calculation.to_dict())

            # Only replace history after all rows are valid.
            self._history = pd.DataFrame(
                calculations,
                columns=self.COLUMNS,
            )

        except (
            OSError,
            UnicodeError,
            ValueError,
            TypeError,
            pd.errors.ParserError,
            pd.errors.EmptyDataError,
            OperationError,
        ) as exc:
            raise HistoryError(
                f"Failed to load history: {exc}"
            ) from exc

    def replace(self, history: pd.DataFrame) -> None:
        """Replace history with a copy of another DataFrame."""
        replacement = history.copy().reset_index(drop=True)

        # Support older history snapshots without timestamps.
        if "timestamp" not in replacement.columns:
            replacement["timestamp"] = datetime.now(
                timezone.utc
            ).isoformat(timespec="seconds")

        self._history = replacement.reindex(columns=self.COLUMNS)

    def is_empty(self) -> bool:
        return self._history.empty

    def __len__(self) -> int:
        return len(self._history)
