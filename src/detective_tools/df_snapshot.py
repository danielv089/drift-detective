import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

class DataFrameSnapshot:

    def __init__(self, df: pd.DataFrame = None, filepath: str = None, table_name: str = None):
        if df is not None:
            self.df = df
            self.filepath = filepath if filepath else "unknown"
            self.name = table_name if table_name else "unknown"
        elif filepath is not None:
            self.df = pd.read_csv(filepath)
            self.filepath = filepath
            self.name = table_name if table_name else Path(filepath).name
        else:
            raise ValueError("You must provide either a DataFrame or a CSV file path.")
        
        self.version=1
        self.snapshot_timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")

    def __repr__(self):
        return f"DfSnapshot(name={self.name}, filepath={self.filepath}, version={self.version}, snapshot_time={self.snapshot_timestamp})"
        
    def get_columns(self):
        return list(self.df.columns)
    
    def num_columns(self):
        return len(self.df.columns)
    
    def num_rows(self):
        return len(self.df)

    def get_schema(self):
        schema = {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        return schema
    
    def snapshot_to_dict(self):
            snapshot = {
                "table_name": self.name,
                "filepath": self.filepath,
                "timestamp": self.snapshot_timestamp,
                "version": self.version,
                "column_count": self.num_columns(),
                "row_count": self.num_rows(),
                "schema": self.get_schema(),
                }
            return snapshot

    def snapshot_to_json(self):
        snapshot_data=self.snapshot_to_dict()
        return json.dumps(snapshot_data, indent=4)
    
    def save_snapshot(self):
        snapshot_data = self.snapshot_to_dict()
        os.makedirs(f"snapshots/{self.name}", exist_ok=True)
        snapshot_file = f"snapshots/{self.name}/{self.name}_v{self.version}_{self.snapshot_timestamp}.json"

        with open(snapshot_file, "w") as f:
            json.dump(snapshot_data, f, indent=4)


