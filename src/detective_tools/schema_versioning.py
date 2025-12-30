import json
from pathlib import Path

class SchemaVersioning:
    """Class to handle schema versioning for database tables."""

    def __init__(self, table_name: str, snapshots_dir: str):
        self.table_name = table_name
        self.snapshots_dir = Path(snapshots_dir)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

        self.columns_removed = []
        self.columns_added = []

    def get_columns_removed(self):
        return self.columns_removed
        
    def get_columns_added(self):
         return self.columns_added
    
    def versioning(self, current_schema: dict):

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
        current_schema=current_schema

        if last_schema != current_schema:
            self.columns_removed = [col for col in last_schema if col not in current_schema]
            self.columns_added = [col for col in current_schema if col not in last_schema]
            return last_version + 1
        
        return last_version

        
        