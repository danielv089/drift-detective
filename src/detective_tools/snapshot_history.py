import json
from pathlib import Path

class SnapshotHistory:

    def __init__(self, table_name: str, snapshots_dir: str):
        self.table_name = table_name
        self.snapshots_dir = Path(snapshots_dir) / table_name
        self.snapshots_list = self.list_snapshots()
        self.versions= self.list_versions()

    def __repr__(self):
        return (
            f"SnapshotHistory(table_name={self.table_name}, "
            f"snapshots_dir={self.snapshots_dir}, "
            f"total_snapshots={len(self.snapshots_list)})"
        )

    def list_snapshots(self):
        if not self.snapshots_dir.exists():
            return []
        return sorted(
            [p for p in self.snapshots_dir.iterdir() if p.is_file() and p.suffix == ".json"]
        )
    
    def list_versions(self):
        versions = []
        for snapshot_file in self.snapshots_list:
            with open(snapshot_file, "r") as f:
                snapshot = json.load(f)
                versions.append(snapshot["version"])
        return versions
    
    def get_version(self, version: int):
        for snapshot_file in self.snapshots_list:
            with open(snapshot_file, "r") as f:
                snapshot = json.load(f)
                if snapshot["version"] == version:
                    return snapshot
        return None
        
    def timeline(self):

        if not self.snapshots_list:
            print("No snapshots found.")
            return

        snapshots = []
        for snapshot_file in self.snapshots_list:
            with open(snapshot_file, "r") as f:
                snapshots.append(json.load(f))

        snapshots.sort(key=lambda s: s["version"])

        print(f"\nSnapshot Timeline for table: {self.table_name}")
        print("─" * 55)

        for snapshot in snapshots:
            version = snapshot["version"]
            timestamp = snapshot["timestamp"]
            column_count = snapshot["column_count"]
            row_count = snapshot["row_count"]

            print(f"\nv{version}  ●  {timestamp}")
            print(f"    │ columns: {column_count}")
            print(f"    │ rows: {row_count}")

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
    
