import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

class DfSnapshot:

    def __init__(self, **kwargs):
        
        df = kwargs.get("df", None)
        filepath = kwargs.get("filepath", None)
        table_name = kwargs.get("table_name", None)

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
        self.snapshot_timestamp=datetime.now().isoformat()
        
    def check_columns(self):
        return list(self.df.columns)
    
    def num_columns(self):
        return len(self.df.columns)
    
    def num_rows(self):
        return len(self.df)

    def check_schema(self):
        schema = {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        return schema
    
    def snapshot_to_dict(self):
            snapshot = {
                "table_name": self.name,
                "filepath": self.filepath,
                "snapshot_time": self.snapshot_timestamp,
                "version": self.version,
                "column_count": self.num_columns(),
                "row_count": self.num_rows(),
                "schema": self.check_schema(),
                }
            return snapshot

    def snapshot_to_json(self):
        snapshot_data=self.snapshot_to_dict()
        return json.dumps(snapshot_data, indent=4)


