from datetime import datetime
import json
from pathlib import Path
from typing import Optional

import pandas as pd
import psycopg2
from psycopg2 import sql

from .snapshot_base import Snapshot
from .schema_versioning import SchemaVersioning
from .snapshot_data_model import SnapshotDataModel

class PsqlSnapshot(Snapshot):


    def __init__(self, table_name:str, connection_params: dict, snapshots_dir:str= "snapshots"):
        if not table_name and connection_params:
            raise ValueError("Table name and connection parameters must be provided.")
        
        super().__init__(table_name)
        self.connection_params= connection_params

        self._make_connection()

        self.snapshots_dir = Path(snapshots_dir) / self.table_name
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

        self.current_schema: Optional[dict[str, str]] = None
        self._version: Optional[int] = None
        self.filepath= self.get_filepath()
        self._columns_added: list[str] = []
        self._snapshot_timestamp: Optional[datetime] = None
        self._columns_removed: list[str] = []

    def _make_connection(self):

        try:
            self.conn=psycopg2.connect(**self.connection_params)
            self.cursor=self.conn.cursor()
        except Exception as e:
            raise ConnectionError("Failed to connect to PostgreSQL database.") from e
    
    def __repr__(self):
        return f"PsqlSnapshot(table_name={self.table_name})"
    
    def num_columns(self) -> int:
        query= sql.SQL("SELECT * FROM {} LIMIT 0").format(sql.Identifier(self.table_name))
        self.cursor.execute(query)
        return len(self.cursor.description)
    
    def num_rows(self) -> int:
        query= sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(self.table_name))
        self.cursor.execute(query)
        result= self.cursor.fetchone()
        return result[0] if result else 0
    

    def get_schema(self) -> dict[str, str]:
        query = sql.SQL(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = {table}"
        ).format(table=sql.Literal(self.table_name))

        self.cursor.execute(query)
        columns = self.cursor.fetchall()
        schema = {col[0]: col[1] for col in columns}
        return schema

    
    def get_filepath(self) -> Path:
        host = self.connection_params.get("host", "localhost")
        port = self.connection_params.get("port", 5432)
        dbname = self.connection_params.get("dbname", "unknown_db")
        user = self.connection_params.get("user", "unknown_user")
        

        pseudo_path = f"{host}_{port}_{dbname}_{user}"
        self.filepath = pseudo_path
        return self.filepath
    
    def compute_snapshot(self) -> None:
        """Compute snapshot details including versioning and schema changes."""
        self._snapshot_timestamp= datetime.now()

        self.current_schema= self.get_schema()

        versioning = PsqlSchemaVersioning(self.table_name, self.snapshots_dir)
        self._version=versioning.versioning(self.current_schema)
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
            schema=self.current_schema,
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

