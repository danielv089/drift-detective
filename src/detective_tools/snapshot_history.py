import json
from pathlib import Path
from collections.abc import Mapping

class SnapshotHistory(Mapping):

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

    def timeline(self):
        if not self._index:
            print("No snapshots found.")
            return

        print(f"\nSnapshot Timeline for table: {self.table_name}")
        print("─" * 55)

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

        print("─" * 55 + "\n")
    
