import json
from pathlib import Path
from snapshot_history import SnapshotHistory

class SnapshotDiff:

    def __init__(self, history, old_snapshot, new_snapshot):
        self.history = SnapshotHistory(history)
        self.old_snapshot = self.history[old_snapshot]
        self.new_snapshot = self.history[new_snapshot]

    def added_columns(self):
        pass

    def removed_columns(self):
        pass
