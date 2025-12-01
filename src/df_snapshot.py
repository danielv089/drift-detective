import pandas as pd
import json
from pathlib import Path
from datetime import datetime

class DfSnapshot:

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
        
    def check_columns(self):
        return list(self.df.columns)
    
    def num_columns(self):
        return len(self.df.columns)
    
    def num_rows(self):
        return len(self.df)

    def check_schema(self):
        schema = {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        return schema
    
    def snapshot(self):
            snapshot = {
                "table_name": self.name,
                "filepath": self.filepath,
                "snapshot_time": datetime.now().isoformat(),
                "version": self.version,
                "column_count": self.num_columns(),
                "row_count": self.num_rows(),
                "schema": self.check_schema(),
                }
            
            return json.dumps(snapshot, indent=4)

