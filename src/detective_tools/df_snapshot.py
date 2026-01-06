from datetime import datetime
import json
from pathlib import Path
from typing import Optional

import pandas as pd

from .snapshot_base import Snapshot
from .schema_versioning import DfSchemaVersioning
from .snapshot_data_model import SnapshotDataModel

class DfSnapshot(Snapshot):
    """Class to create and manage snapshots of pandas DataFrames.
    Attributes:
        table_name (str): Name of the DataFrame/table.
        df (pd.DataFrame): The pandas DataFrame to snapshot.
        filepath (str): Optional file path from which the DataFrame was loaded.
        snapshots_dir (str): Directory to store snapshots
        """

    def __init__(self, table_name:str, df: Optional[pd.DataFrame]= None, filepath: Optional[str]=None, snapshots_dir:str= "snapshots"):
        if not table_name:
            raise ValueError("Table name must be provided.")
        
        super().__init__(table_name)

        self._load_data(df,filepath)

        self.snapshots_dir = Path(snapshots_dir) / self.table_name
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

        self.current_schema: Optional[dict[str, str]] = None
        self._version: Optional[int] = None
        self._columns_added: list[str] = []
        self._columns_removed: list[str] = []
        self._snapshot_timestamp: Optional[datetime] = None

    def _load_data(self, df: Optional[pd.DataFrame], filepath: Optional[str]) -> None:
        """Load DataFrame from provided df or CSV file path."""
        if df is not None:
            self.df= df
            self.filepath=filepath or "Unknown"
            return

        if filepath is not None:
            path= Path(filepath)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {filepath}")

            try:
                self.df=pd.read_csv(path)
            except Exception as e:
                raise ValueError(f"Failed to load CSV: {filepath}") from e

            self.filepath = filepath
            return 

        raise ValueError("You must provide either a DataFrame or a CSV file path.")

    def __repr__(self):
        return f"DfSnapshot(name={self.table_name}, filepath={self.filepath}, version={self._version}, snapshot_time={self._snapshot_timestamp})"
    
    #Pandas derived helper functions
    #-----------------------------------------
    def num_columns(self) -> int:
        return len(self.df.columns)
    
    def num_rows(self) -> int:
        return len(self.df)

    def get_schema(self) -> dict[str, str]:
        schema = {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        return schema

    # Snapshot creation and saving
    #-----------------------------------------

    def compute_snapshot(self) -> None:
        """Compute snapshot details including versioning and schema changes."""
        self._snapshot_timestamp= datetime.now()

        self._current_schema= self.get_schema()

        versioning = DfSchemaVersioning(self.table_name, self.snapshots_dir)
        self._version=versioning.versioning(self._current_schema)
        self._columns_added= versioning.get_columns_added()
        self._columns_removed= versioning.get_columns_removed()

    def create_snapshot(self) -> SnapshotDataModel:
        """Create a snapshot data model instance.
        Returns:
            SnapshotDataModel: An instance containing snapshot details.
        """
        snapshot = SnapshotDataModel(
            table_name=self.table_name,
            filepath=self.filepath,
            timestamp=datetime.now(),
            version=self._version,
            column_count=self.num_columns(),
            row_count=self.num_rows(),
            schema=self._current_schema,
            columns_added=self._columns_added,
            columns_removed=self._columns_removed
        )
        return snapshot
    
    def save_snapshot(self) -> Path:
        """Save the snapshot data model to a JSON file.
        """
    
        snapshot=self.create_snapshot()
        snapshot_file=self.snapshots_dir / f"{self.table_name}_v{self._version}_{self._snapshot_timestamp}.json"

        with open(snapshot_file, "w") as f:
            json.dump(snapshot.to_dict(), f, indent=4)

        return snapshot_file


