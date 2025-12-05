import os

class SnapshotStore:


    def snapshot_to_json(self):
        snapshot_data=self.snapshot_to_json()
        os.makedirs("snapshots", exist_ok=True)
        snapshot_file = f"snapshots/{self.name}_snapshot_v{self.version}_{self.snapshot_timestamp}.json"
        with open(snapshot_file, "w") as f:
            json.dump(snapshot_data, f, indent=4)
