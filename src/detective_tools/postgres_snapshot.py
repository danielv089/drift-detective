from datetime import datetime
import json
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from .schema_versioning import SchemaVersioning
from .snapshot_base import Snapshot
from .snapshot_data_model import SnapshotDataModel
class PsqlSnapshot(Snapshot):
    """Class to handle PostgreSQL table snapshots.
    Attributes:
        table_name (str): Name of the PostgreSQL table.
        connection_string (str): Connection string for the PostgreSQL database.
        snapshots_dir (str): Directory to store snapshots.
    """

    def __init__(self, table_name:str, connection_string: str, snapshots_dir:str= "snapshots"):
        if not table_name and connection_string:
            raise ValueError("Table name and connection parameters must be provided.")
        
        super().__init__(table_name)
        self.connection_string= connection_string

        self._connect_postgres()

        self.snapshots_dir = Path(snapshots_dir) / self.table_name
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

        self.current_schema: Optional[dict[str, str]] = None
        self._version: Optional[int] = None
        self.filepath= self.get_filepath()
        self._columns_added: list[str] = []
        self._snapshot_timestamp: Optional[datetime] = None
        self._columns_removed: list[str] = []

    def _connect_postgres(self) -> None:
        """Establish connection to the PostgreSQL database."""
        try:
            self.engine = create_engine(self.connection_string)
        except Exception as e:
            raise ConnectionError("Failed to connect to PostgreSQL database.") from e

    def __repr__(self) -> str:
        return f"PsqlSnapshot(table_name={self.table_name})"

 
    #Helper functions
    #-----------------------------------------
    def num_columns(self) -> int:
        """Get the number of columns in the PostgreSQL table."""
        with self.engine.connect() as conn:
            result= conn.execute(text(f"SELECT * FROM {self.table_name} LIMIT 0;"))
            num_col = len(result.keys())
        return num_col

    def num_rows(self) -> int:
        """Get the number of rows in the PostgreSQL table."""
        with self.engine.connect() as conn:
            result= conn.execute(text(f"SELECT COUNT(*) FROM {self.table_name}"))
            num_rows=result.scalar()
        return num_rows

    def get_schema(self) -> dict:
        """Retrieve the schema of the PostgreSQL table.
        Returns:
            dict: A dictionary mapping column names to their data types.
        """
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = :table
                  AND table_schema = 'public'
                """),
                {"table": self.table_name}
            )

            schema = {row[0].strip(): row[1] for row in result.fetchall()}
            return schema

    def get_filepath(self) -> str:
        """Generate a pseudo-filepath for the PostgreSQL table snapshot."""
        url=make_url(self.connection_string)

        host = url.host or "localhost"
        port = url.port or 5432
        dbname = url.database or "unknown_db"
        pseudo_path = f"{host}_{port}_{dbname}_{self.table_name}"

        self.filepath=pseudo_path
        return self.filepath
    
        # Snapshot creation and saving
    #-----------------------------------------

    def compute_snapshot(self) -> None:
        """Compute snapshot details including versioning and schema changes."""
        self._snapshot_timestamp= datetime.now()

        self.current_schema= self.get_schema()

        versioning = SchemaVersioning(self.table_name, self.snapshots_dir)
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
