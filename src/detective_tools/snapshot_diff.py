from .snapshot_history import SnapshotHistory

class SnapshotDiff:

    def __init__(self, history, old_snapshot, new_snapshot):
        self.history = history
        self.old_snapshot = self.history[old_snapshot]
        self.new_snapshot = self.history[new_snapshot]

    def added_columns(self):
        old_cols = set(self.old_snapshot.get("schema", []))
        new_cols = set(self.new_snapshot.get("schema", []))
        return list(new_cols - old_cols)

    def removed_columns(self):
        old_cols = set(self.old_snapshot.get("schema", []))
        new_cols = set(self.new_snapshot.get("schema", []))
        return list(old_cols - new_cols)
    
    def dict_diff(self):
        report = {
            "old_snapshot_version": self.old_snapshot["version"],
            "old_snapshot_timestamp": self.old_snapshot["timestamp"],
            "new_snapshot_version": self.new_snapshot["version"],
            "new_snapshot_timestamp": self.new_snapshot["timestamp"],
            "added_columns": self.added_columns(),
            "removed_columns": self.removed_columns(),
        }
        return report

    def pretty_diff(self):
        print(f"\nSnapshot Diff for table: {self.history.table_name}")
        print("─" * 55)
        print(f"Old snapshot v{self.old_snapshot['version']}  ●  {self.old_snapshot['timestamp']}")
        print(f"New snapshot v{self.new_snapshot['version']}  ●  {self.new_snapshot['timestamp']}")
        print(f"Added columns (new → old): {', '.join(self.added_columns()) or f"No added column(s)"}")
        print(f"Removed columns (new → old): {', '.join(self.removed_columns()) or f"No removed column(s)"}")
        print("─" * 55 + "\n")
