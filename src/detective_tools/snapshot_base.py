from abc import ABC, abstractmethod

class Snapshot(ABC):
    """Abstract base class for data snapshots."""

    def __init__(self, table_name: str):
        self.table_name = table_name

    @abstractmethod
    def num_columns(self):
        pass

    @abstractmethod
    def num_rows(self):
        pass

    @abstractmethod
    def get_schema(self):
        pass

    @abstractmethod
    def snapshot_to_dict(self):
        pass

    @abstractmethod
    def snapshot_to_json(self):
        pass

    @abstractmethod
    def save_snapshot(self):
        pass