from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass(frozen=True, order=True)
class SnapshotDataModel:
    """Data model representing a snapshot of a DataFrame."""

    table_name: str
    filepath: str
    timestamp: datetime
    verion: int
    column_count: int
    row_count: int
    schema: Dict[str, str]
    columns_added: List[str]
    columns_removed: List[str]

    def to_dict(self) -> Dict:
        """Convert the SnapshotDataModel to a dictionary."""

        return {
            "table_name": self.table_name,
            "filepath": self.filepath,
            "timestamp": self.timestamp.isoformat(),
            "version": self.verion,
            "column_count": self.column_count,
            "row_count": self.row_count,
            "schema": self.schema,
            "columns_added": self.columns_added,
            "columns_removed": self.columns_removed,
        }
    