import os

class SnapshotStore:

    def __init__(self, store_path):
        self.store=store_path
        self.store.makedirs(self.store, exist_ok=True)


    def load_snapshot(self):
        pass
    

    def latest_snapshot(self):
        pass

    def list_snapshots(self):
        pass

    def versioning_snapshot(self):
        pass

    
