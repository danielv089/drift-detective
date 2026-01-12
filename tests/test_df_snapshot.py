import json
from pathlib import Path

import pandas as pd
import pytest

from detective_tools.df_snapshot import DfSnapshot
from detective_tools.schema_versioning import DfSchemaVersioning


#Fixtures for test data
#-----------------------------
@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["a", "b", "c"]
    })

@pytest.fixture
def empty_df():
    return pd.DataFrame()

@pytest.fixture
def sample_csv_file(tmp_path, sample_df):
    csv_file= tmp_path / "data.csv"
    sample_df.to_csv(csv_file, index=False)
    return csv_file

#Data Loading Tests
#-----------------------------
def test_load_from_dataframe(sample_df, tmp_path):
    snapshot= DfSnapshot(table_name="users", df=sample_df, snapshots_dir=tmp_path)

    assert snapshot.df.equals(sample_df)
    assert snapshot.filepath == "Unknown"

def test_load_from_csv_file(sample_csv_file, sample_df, tmp_path):
    snapshot= DfSnapshot(table_name="users", filepath=str(sample_csv_file), snapshots_dir=tmp_path)

    assert snapshot.df.equals(sample_df)
    assert snapshot.filepath == str(sample_csv_file)

#Snapshot computation and saving tests
#-----------------------------
def test_load_without_dataframe_or_filepath(tmp_path):
    with pytest.raises(ValueError, match="You must provide either a DataFrame or a CSV file path."):
        DfSnapshot(table_name="users", snapshots_dir=tmp_path)

def test_table_name_required(sample_df, tmp_path):
    with pytest.raises(ValueError, match="Table name must be provided."):
        DfSnapshot(table_name="", df=sample_df, snapshots_dir=tmp_path)


def test_num_rows_and_columns(sample_df, tmp_path):
    snapshot= DfSnapshot(table_name="users", df=sample_df, snapshots_dir=tmp_path)

    assert snapshot.num_rows() == 3
    assert snapshot.num_columns() == 2

def test_get_schema(sample_df, tmp_path):
    snapshot= DfSnapshot(table_name="users", df=sample_df, snapshots_dir=tmp_path)

    expected_schema= {
        "id": "int64",
        "name": "object"
    }

    assert snapshot.get_schema() == expected_schema

def test_empty_dataframe(empty_df, tmp_path):
    snapshot= DfSnapshot(table_name="empty_table", df=empty_df, snapshots_dir=tmp_path)

    assert snapshot.num_rows() == 0
    assert snapshot.num_columns() == 0
    assert snapshot.get_schema() == {}

def test_compute_snapshot(sample_df, tmp_path):
    snapshot= DfSnapshot(table_name="users", df=sample_df, snapshots_dir=tmp_path)
    snapshot.compute_snapshot()

    assert snapshot._snapshot_timestamp is not None
    assert snapshot._version is not None
    assert isinstance(snapshot._columns_added, list)
    assert isinstance(snapshot._columns_removed, list)
    assert snapshot._current_schema is not None

def test_save_snaspshot(sample_df, tmp_path):
    snapshot= DfSnapshot(table_name="users", df=sample_df, snapshots_dir=tmp_path)
    snapshot.compute_snapshot()
    snapshot.save_snapshot()

    snapshot_files= list((tmp_path / "users").glob("*.json"))
    assert len(snapshot_files) == 1

    with open(snapshot_files[0], "r") as f:
        data= json.load(f)

    assert data["version"] == snapshot._version
    assert data["schema"] == snapshot.get_schema()