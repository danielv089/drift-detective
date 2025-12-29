import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

from snapshot_base import Snapshot

class DfSnapshot(Snapshot):

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
        self.snapshot_timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
        self.columns_removed=[]
        self.columns_added=[]
        self.version= self.schema_versioning()

    def __repr__(self):
        return f"DfSnapshot(name={self.table_name}, filepath={self.filepath}, version={self.version}, snapshot_time={self.snapshot_timestamp})"
    
    def num_columns(self):
        return len(self.df.columns)
    
    def num_rows(self):
        return len(self.df)

    def get_schema(self):
        schema = {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        return schema
    
    def snapshot_to_dict(self):
            snapshot = {
                "table_name": self.table_name,
                "filepath": self.filepath,
                "timestamp": self.snapshot_timestamp,
                "version": self.version,
                "column_count": self.num_columns(),
                "row_count": self.num_rows(),
                "schema": self.get_schema(),
                "columns_added": self.columns_added,
                "columns_removed": self.columns_removed
                }
            return snapshot

    def snapshot_to_json(self):
        snapshot_data=self.snapshot_to_dict()
        return json.dumps(snapshot_data, indent=4)
    
    def save_snapshot(self):
        snapshot_data = self.snapshot_to_dict()
        snapshot_file = self.snapshots_dir / f"{self.table_name}_v{self.version}_{self.snapshot_timestamp}.json"

        with open(snapshot_file, "w") as f:
            json.dump(snapshot_data, f, indent=4)

        return snapshot_file

    def schema_versioning(self):
        snapshot_files=list(self.snapshots_dir.glob(f"{self.table_name}_v*_*.json"))

        if not snapshot_files:
            return 1
        
        last_snapshot=None
        last_version=0

        for f in snapshot_files:
            with open(f,"r") as jf:
                data=json.load(jf)
                version=data.get("version",0)
                if version>last_version:
                    last_version=version
                    last_snapshot=data

        last_schema=last_snapshot.get("schema",{})
        current_schema=self.get_schema()

        if last_schema != current_schema:
            self.columns_removed = [col for col in last_schema if col not in current_schema]
            self.columns_added = [col for col in current_schema if col not in last_schema]
            return last_version + 1
        
        return last_version


