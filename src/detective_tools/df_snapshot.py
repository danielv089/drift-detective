from datetime import datetime
import json
import os
from pathlib import Path

import pandas as pd

from .snapshot_base import Snapshot
from .schema_versioning import SchemaVersioning

class DfSnapshot(Snapshot):
    """Class to create and manage snapshots of pandas DataFrames.
    Attributes:
        table_name (str): Name of the DataFrame/table.
        df (pd.DataFrame): The pandas DataFrame to snapshot.
        filepath (str): Optional file path from which the DataFrame was loaded.
        snapshots_dir (str): Directory to store snapshots
        """

    def __init__(self, table_name:str, df: pd.DataFrame = None, filepath: str = None, snapshots_dir: str="snapshots" ):

        if not table_name:
            raise ValueError("Table name must be provided.")
        
        super().__init__(table_name)
        
        if df is not None:
            self.df = df
            self.filepath = filepath if filepath else "unknown"
        elif filepath is not None:
            self.df = pd.read_csv(filepath)
            self.filepath = filepath
        else:
            raise ValueError("You must provide either a DataFrame or a CSV file path.")
        
        self.snapshots_dir = Path(snapshots_dir) / self.table_name
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self._snapshot_timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")

        self.current_schema=self.get_schema()
        
        versioning = SchemaVersioning(self.table_name, self.snapshots_dir)
        self._version=versioning.versioning(self.current_schema)
        self._columns_added= versioning.get_columns_added()
        self._columns_removed= versioning.get_columns_removed()

    def __repr__(self):
        return f"DfSnapshot(name={self.table_name}, filepath={self.filepath}, version={self._version}, snapshot_time={self._snapshot_timestamp})"
    
    def num_columns(self):
        return len(self.df.columns)
    
    def num_rows(self):
        return len(self.df)

    def get_schema(self):
        schema = {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        return schema
    
    def snapshot_to_dict(self):
            """Create a dictionary representation of the snapshot.
            Returns:
                dict: A dictionary containing snapshot details.
            """
            snapshot = {
                "table_name": self.table_name,
                "filepath": self.filepath,
                "timestamp": self._snapshot_timestamp,
                "version": self._version,
                "column_count": self.num_columns(),
                "row_count": self.num_rows(),
                "schema": self.current_schema,
                "columns_added": self._columns_added,
                "columns_removed": self._columns_removed
                }
            return snapshot

    def snapshot_to_json(self):
        """Create a JSON representation of the snapshot.
        Returns:
            str: A JSON string containing snapshot details.
        """
        snapshot_data=self.snapshot_to_dict()
        return json.dumps(snapshot_data, indent=4)
    
    def save_snapshot(self):
        """Save the snapshot to a versioned JSON file.
         Returns: The path to the saved snapshot file.
         """
        snapshot_data = self.snapshot_to_dict()
        snapshot_file = self.snapshots_dir / f"{self.table_name}_v{self._version}_{self._snapshot_timestamp}.json"

        with open(snapshot_file, "w") as f:
            json.dump(snapshot_data, f, indent=4)

        return snapshot_file


