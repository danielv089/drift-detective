import json
from pathlib import Path

import pytest
import pandas as pd

from detective_tools.df_snapshot import DfSnapshot
from detective_tools.schema_versioning import DfSchemaVersioning

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

def test_load_from_dataframe(sample_df, tmp_path):
    snapshot= DfSnapshot(table_name="users", df=sample_df, snapshots_dir=tmp_path)

    assert snapshot.df.equals(sample_df)
    assert snapshot.filepath == "Unknown"

def test_load_from_csv_file(sample_csv_file, sample_df, tmp_path):
    snapshot= DfSnapshot(table_name="users", filepath=str(sample_csv_file), snapshots_dir=tmp_path)

    assert snapshot.df.equals(sample_df)
    assert snapshot.filepath == str(sample_csv_file)


