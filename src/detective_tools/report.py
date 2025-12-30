from .snapshot_history import SnapshotHistory
from .snapshot_diff import SnapshotDiff
class SchemaReport:

    def __init__(self, history, diff=None):
        self.history = history
        self.diff = diff

        self._latest_snapshot = self.history[max(self.history)]
        self._first_snapshot = self.history[1]

    def struct_report(self):
        report = {
            "table_name": self.history.table_name,
            "snapshots_directory": self.history.snapshots_dir,
            "latest_snapshot_version": self._latest_snapshot["version"],
            "available_versions": self.history.versions(),
            "total_snapshots": len(self.history),
            "first_snapshot_created": self._first_snapshot["timestamp"],
            "latest_snapshot_created": self._latest_snapshot["timestamp"],
        }

        timeline = self.history.dict_timeline()

        latest_snapshot = self.history.dict_latest()

        if self.diff:
            diff_snapshot = self.diff.dict_diff()

        return report, timeline, latest_snapshot, diff_snapshot if self.diff else None
    
    def pretty_report(self, main:bool, add_latest:bool = False, add_timeline:bool = False, add_diff:bool = False):
        
        print(f"\nSchema Change Report for table: {self.history.table_name}")
        print("─" * 60)
        print(f"Snapshots directory: {self.history.snapshots_dir}")
        print(f"Latest snapshot version: {self._latest_snapshot["version"]} ")
        print(f"Available versions: {', '.join(map(str, self.history.versions()))}")
        print(f"Total snapshots: {len(self.history)}")
        print(f"First snapshot Created: {self._first_snapshot['timestamp']}")
        print(f"Latest snapshot Created: {self._latest_snapshot['timestamp']}")
        print("─" * 60)

        if add_latest:
            self.history.pretty_latest()

            if add_timeline:
                self.history.pretty_timeline()

                if add_diff and self.diff:
                    self.diff.pretty_diff()
