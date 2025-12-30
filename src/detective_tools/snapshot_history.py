import json
from pathlib import Path

from collections.abc import Mapping

class SnapshotHistory(Mapping):
    """Manages the history of snapshots for a specific table.
    Each snapshot is stored as a JSON file in a directory structure like:
    snapshots/
        table_name/
            snapshot_v1.json
            snapshot_v2.json
    Attributes:
        table_name (str): The name of the table.
        snapshots_dir (Path): The directory where snapshots are stored.
    Methods:
        __getitem__(version): Retrieve a snapshot by its version number.
        __iter__(): Iterate over available snapshot versions.
        __len__(): Get the total number of snapshots.   
            ..."""

    def __init__(self, table_name: str, snapshots_dir: str):
        self.table_name = table_name
        self.snapshots_dir = Path(snapshots_dir) / table_name

        self._snapshot_files = self._list_snapshots()
        self._index = self._build_index()

    def __repr__(self):
        return (
            f"SnapshotHistory(table_name={self.table_name}, "
            f"snapshots_dir={self.snapshots_dir}, "
            f"total_snapshots={len(self)})"
        )

    def _list_snapshots(self):
        if not self.snapshots_dir.exists():
            return []
        return sorted(
            p for p in self.snapshots_dir.iterdir()
            if p.is_file() and p.suffix == ".json"
        )

    def _build_index(self):
        index = {}
        for path in self._snapshot_files:
            with open(path, "r") as f:
                snapshot = json.load(f)
                index[snapshot["version"]] = path
        return index

    def __getitem__(self, version: int):
        version = int(version)
        try:
            path = self._index[version]
        except KeyError:
            raise KeyError(
                f"Version {version} not found for table {self.table_name}. "
                f"Available versions: {list(self._index)}"
            )

        with open(path, "r") as f:
            return json.load(f)

    def __iter__(self):
        return iter(sorted(self._index))

    def __len__(self):
        return len(self._index)

    def versions(self):
        return sorted(self._index)
    
    def dict_timeline(self):
        """Returns the snapshot timeline as a list of dictionaries.
        Returns:
            List[Dict]: A list of dictionaries representing the snapshot timeline
        """
        timeline = []

        for version in self:
            snapshot = self[version]
            entry = {
                "version": version,
                "timestamp": snapshot["timestamp"],
                "column_count": len(snapshot.get("schema", [])),
                "row_count": snapshot.get("row_count", 0),
                "columns_added": snapshot.get("columns_added", []),
                "columns_removed": snapshot.get("columns_removed", []),
            }
            timeline.append(entry)

        return timeline

    def pretty_timeline(self):
        """Prints a human-readable snapshot timeline to the console."""
        if not self._index:
            print("No snapshots found.")
            return

        print(f"\nSnapshot Timeline for table: {self.table_name}")
        print("─" * 60)

        for version in self:
            snapshot = self[version]

            print(f"\nv{version}  ●  {snapshot['timestamp']}")
            print(f"    │ columns: {snapshot['column_count']}")
            print(f"    │ rows: {snapshot['row_count']}")

            if version == 1:
                print("    │ initial snapshot")
                continue

            added = snapshot.get("columns_added", [])
            removed = snapshot.get("columns_removed", [])

            if added:
                print(f"    │ + added columns: {', '.join(added)}")
            if removed:
                print(f"    │ - removed columns: {', '.join(removed)}")
            if not added and not removed:
                print("    │ no schema changes")

        print("─" * 60 + "\n")

    def dict_latest(self):
        """Returns the latest snapshot as a dictionary.
        Returns:
            Dict: A dictionary representing the latest snapshot
            """
        
        all_columns_added=[]
        all_columns_removed=[]

        for version in self:
            snapshot=self[version]

            all_columns_added.extend(snapshot.get("columns_added",[]))
            all_columns_removed.extend(snapshot.get("columns_removed",[]))

        latest_version=max(self._index)
        latest_snapshot= self[latest_version]
        latest_snapshot_columns= latest_snapshot.get("schema")

        report={
            "version": latest_version,
            "timestamp": latest_snapshot["timestamp"],
            "column_count": latest_snapshot["column_count"],
            "row_count": latest_snapshot["row_count"],
            "current_columns": latest_snapshot_columns,
            "all_added_columns": all_columns_added,
            "all_removed_columns": all_columns_removed,
        }

        return report

    def pretty_latest(self):
        """Prints a human-readable latest snapshot report to the console."""
        all_columns_added=[]
        all_columns_removed=[]

        for version in self:
            snapshot=self[version]

            all_columns_added.extend(snapshot.get("columns_added",[]))
            all_columns_removed.extend(snapshot.get("columns_removed",[]))

        latest_version=max(self._index)
        latest_snapshot= self[latest_version]
        latest_snapshot_columns= latest_snapshot.get("schema")

        print(f"\n Latest Snapshot for table: {self.table_name}")
        print("─" * 60)
        print(f"v{version}  ●  {latest_snapshot['timestamp']}")
        print(f"    |   columns: {latest_snapshot['column_count']}")
        print(f"    |   rows: {latest_snapshot['row_count']}")
        print(f"    |   current columns: {', '.join(latest_snapshot_columns)}")
        print(f"    | + all added columns: {', '.join(all_columns_added)}")
        print(f"    │ - all removed columns: {', '.join(all_columns_removed)}")
        print("─" * 60)
    
