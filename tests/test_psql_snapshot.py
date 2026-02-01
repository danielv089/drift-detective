import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from detective_tools.postgres_snapshot import PsqlSnapshot
from detective_tools.schema_versioning import SchemaVersioning


#Fixtures for test data
#-----------------------------
# Database connection parameters
# Need to be provided for testing

USER= "username"
PASSWORD= "password"
HOST= "localhost"
PORT= "5432"
DBNAME= "database_name"

@pytest.fixture(scope="session")
def connection_string():
    return f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"

@pytest.fixture(scope="session")
def setup_test_table(connection_string):
    engine = create_engine(connection_string)
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name VARCHAR(50));"))
        conn.execute(text("INSERT INTO users (name) VALUES ('Alice'), ('Bob'), ('Charlie');"))
    yield
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS users;"))

#Data Loading Tests
#-----------------------------

def test_table_name_and_connection_string_required(setup_test_table):
    with pytest.raises(ConnectionError, match="Failed to connect to PostgreSQL database."):
        PsqlSnapshot(table_name="", connection_string="")

def test_connect_postgres_success(setup_test_table, connection_string):
    snapshot= PsqlSnapshot(table_name="users", connection_string=connection_string)
    assert snapshot.engine is not None

#Snapshot helpers Tests
#-----------------------------

def test_num_columns(setup_test_table, connection_string):
    snapshot= PsqlSnapshot(table_name="users", connection_string=connection_string)
    assert snapshot.num_columns() == 2

def test_num_rows(setup_test_table, connection_string):
    snapshot= PsqlSnapshot(table_name="users", connection_string=connection_string)
    assert snapshot.num_rows() == 3

def test_get_schema(setup_test_table, connection_string):
    snapshot= PsqlSnapshot(table_name="users", connection_string=connection_string)
    expected_schema= {
        "id": "integer",
        "name": "character varying"
    }
    assert snapshot.get_schema() == expected_schema

def test_get_filepath(setup_test_table, connection_string):
    snapshot= PsqlSnapshot(table_name="users", connection_string=connection_string)
    expected_filepath= f"{HOST}_{PORT}_{DBNAME}_users"
    assert snapshot.get_filepath() == expected_filepath

#Snapshot computation and saving tests
#-----------------------------

def test_compute_snapshot(setup_test_table, connection_string):
    snapshot= PsqlSnapshot(table_name="users", connection_string=connection_string)
    snapshot.compute_snapshot()
    
    assert snapshot.current_schema is not None
    assert isinstance(snapshot.current_schema, dict)
    assert snapshot._version is not None
    assert snapshot._snapshot_timestamp is not None

def test_create_snapshot(setup_test_table, connection_string):
    snapshot= PsqlSnapshot(table_name="users", connection_string=connection_string)
    snapshot.compute_snapshot()
    snapshot.create_snapshot()

    assert snapshot.table_name == "users"
    assert snapshot.num_rows() == 3
    assert snapshot.num_columns() == 2
    assert isinstance(snapshot.get_schema(), dict)

def test_save_snapshot(setup_test_table, tmp_path, connection_string):
    snapshot = PsqlSnapshot(table_name="users", connection_string=connection_string, snapshots_dir=tmp_path)
    snapshot.compute_snapshot()
    saved_file = snapshot.save_snapshot()

    assert saved_file.exists()
    assert saved_file.suffix == ".json"

    assert saved_file.parent == tmp_path / "users"

    with saved_file.open("r") as f:
        data = json.load(f)

    assert data["table_name"] == "users"
    assert data["row_count"] == 3
    assert data["column_count"] == 2
    assert isinstance(data["schema"], dict)