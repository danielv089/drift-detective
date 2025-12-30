# Drift Detective Documentation

Drift Detective is a Python library for tracking schema evolution and detecting structural drift in tabular datasets using versioned JSON snapshots.

It is designed for data workflows where table schemas evolve over time.

## Installation

## API Reference

Drift Detective is built around four core components, each responsible for a specific part of schema tracking and reporting:

- DfSnapshot: Captures the schema state of a pandas DataFrame at a specific point in time and stores it as a versioned snapshot.
- SnapshotHistory: Creates a schema evolution timeline listing version and schema changes.
- SnapshotDiff: Compares schema changes between two snapshot versions, listing all added and removed columns across intermediate versions.
- SchemaReport: Integrates all components into a complete report to tell the full story

### Creating Snapshot

Import and initialize dataframe snapshot class. 

```python
from detective_tools import DfSnapshot
import pandas as pd
```
You can create a snapshot either by passing a DataFrame directly or by providing the path to a CSV file.

The table_name argument is required.

```python
#Creating Dataframe
netflix_df = pd.read_csv("netflix_titles.csv")
netflix_df.head(3)

# Assuming you already have a DataFrame called netflix_df
snapshot = DfSnapshot(
    table_name="netflix_titles",  # Name of the table
    df=netflix_df,                # The DataFrame to snapshot
    filepath="netflix_titles.csv" # Optional: original CSV file path
)

# Or using a CSV file path
snapshot = DfSnapshot(
    table_name="netflix_titles",
    filepath="netflix_titles.csv"
)
```

Snapshots are incremental.

Each new snapshot is compared to the previous version, and changes in the schema are automatically detected.

To create a new snapshot, simply call the save_snapshot() method:

```python
#Save a snapshot
snapshot.save_snapshot()
```

Snapshots are stored in 

```bash
└── snapshots
    └── netflix_titles
        ├── netflix_titles_v1_20251230_161527.json
        ├── netflix_titles_v1_20251230_162126.json
        ├── netflix_titles_v2_20251230_163649.json
        └── netflix_titles_v3_20251230_163729.json
```
File names follow the format:

```python
<table_name>_v<version>_<timestamp>.json
```

Each Snapshot contains the following information:

```json
{
    "table_name": "netflix_titles",
    "filepath": "netflix_titles.csv",
    "timestamp": "20251230_161527",
    "version": 1,
    "column_count": 12,
    "row_count": 8807,
    "schema": {
        "show_id": "object",
        "type": "object",
        "title": "object",
        "director": "object",
        "cast": "object",
        "country": "object",
        "date_added": "object",
        "release_year": "int64",
        "rating": "object",
        "duration": "object",
        "listed_in": "object",
        "description": "object"
    },
    "columns_added": [],
    "columns_removed": []
}
```

In order to make  new snapshot you need to call the save_snapshot() method again.

Every time you create a new snapshot, DfSnapshot automatically detects:
- added columns compared to the previous snapshot
- removed columns compared to the previous snapshot
- increments the version number

Version 2 after the removal of one column:

```json
{
    "table_name": "netflix_titles",
    "filepath": "netflix_titles.csv",
    "timestamp": "20251230_163649",
    "version": 2,
    "column_count": 11,
    "row_count": 8807,
    "schema": {
        "show_id": "object",
        "type": "object",
        "director": "object",
        "cast": "object",
        "country": "object",
        "date_added": "object",
        "release_year": "int64",
        "rating": "object",
        "duration": "object",
        "listed_in": "object",
        "description": "object"
    },
    "columns_added": [],
    "columns_removed": [
        "title"
    ]
}
```

Version 3 after the removal of another column:

```json
{
    "table_name": "netflix_titles",
    "filepath": "netflix_titles.csv",
    "timestamp": "20251230_163729",
    "version": 3,
    "column_count": 10,
    "row_count": 8807,
    "schema": {
        "show_id": "object",
        "type": "object",
        "director": "object",
        "cast": "object",
        "country": "object",
        "date_added": "object",
        "release_year": "int64",
        "rating": "object",
        "duration": "object",
        "description": "object"
    },
    "columns_added": [],
    "columns_removed": [
        "listed_in"
    ]
}
```
### Inspecting Snapshot History 

SnapshotHistory allows you to inspect all snapshots of a table, view versions, track schema evolution, and summarize the latest snapshot.

Import and initialize snapshot history class:

```python
from detective_tools import SnapshotHistory
```

Make sure snapshots_dir points to the folder containing the snapshots folder. SnapshotHistory will automatically append the table name internally.

```python
# Create a SnapshotHistory object pointing to the snapshots folder
history = SnapshotHistory(
    table_name="netflix_titles", # Name of the table
    snapshots_dir="docs/snapshots" # Filepath to the snapshots folder
)
```

You can print a human-readable timeline of all snapshots using the pretty_timeline() method:

```python
history.pretty_timeline()
```

Example output:

```bash
Snapshot Timeline for table: netflix_titles
────────────────────────────────────────────────────────────

v1  ●  20251230_162126
    │ columns: 12
    │ rows: 8807
    │ initial snapshot

v2  ●  20251230_163649
    │ columns: 11
    │ rows: 8807
    │ - removed columns: title

v3  ●  20251230_163729
    │ columns: 10
    │ rows: 8807
    │ - removed columns: listed_in
────────────────────────────────────────────────────────────
```

You can also get the timeline as a list of dictionaries using the dict_timeline() method:

```python
history.dict_timeline()

#Example output:

[{'version': 1,
  'timestamp': '20251230_162126',
  'column_count': 12,
  'row_count': 8807,
  'columns_added': [],
  'columns_removed': []},
 {'version': 2,
  'timestamp': '20251230_163649',
  'column_count': 11,
  'row_count': 8807,
  'columns_added': [],
  'columns_removed': ['title']},
 {'version': 3,
  'timestamp': '20251230_163729',
  'column_count': 10,
  'row_count': 8807,
  'columns_added': [],
  'columns_removed': ['listed_in']}]
```
You can print a human-readable output of the lates snapshots using the pretty_latest() method:

```python
history.pretty_latest()
```

Example output:

```bash
Latest Snapshot for table: netflix_titles
────────────────────────────────────────────────────────────
v3  ●  20251230_163729
    |   columns: 10
    |   rows: 8807
    |   current columns: show_id, type, director, cast, country, date_added, release_year, rating, duration, description
    | + all added columns: 
    │ - all removed columns: title, listed_in
────────────────────────────────────────────────────────────
```

You can also get the latest snapshot as a dictionary using the dict_latest() method:

```python
history.dict_latest()

{'version': 3,
 'timestamp': '20251230_163729',
 'column_count': 10,
 'row_count': 8807,
 'current_columns': {'show_id': 'object',
  'type': 'object',
  'director': 'object',
  'cast': 'object',
  'country': 'object',
  'date_added': 'object',
  'release_year': 'int64',
  'rating': 'object',
  'duration': 'object',
  'description': 'object'},
 'all_added_columns': [],
 'all_removed_columns': ['title', 'listed_in']}
 ```

### Comparing Snapshot Versions

SnapshotDiff allows you to compare two snapshot versions of the same table and see which columns were added or removed between them.

The SnapshotDiff class reads all consecutive snapshot versions between the specified old and new snapshots. 

It then lists all columns that were added or removed across these versions, giving a complete view of schema changes over that range.

Import and initialize snapshot history and snapshot difference class:

```python
from detective_tools import SnapshotHistory
from detective_tools import SnapshotDiff
```
Import and initialize snapshot history and snapshot difference class:

The SnapshotDiff class is built on top of SnapshotHistory. 

Therefore, you must first initialize a SnapshotHistory object before you can compare snapshot versions.

```python
# Create a SnapshotHistory object pointing to the snapshots folder
history = SnapshotHistory(
    table_name="netflix_titles", # Name of the table
    snapshots_dir="docs/snapshots" # Filepath to the snapshots folder
)
```

Create the compare object to compare snapshot version 1 and version 3

```python

compare= SnapshotDiff(history, # Snapshot history object
                       1,      # Number of old snapshot version
                       3       # Number of new snapshot version
                       )
```

You can print a human-readable output of the versions compare using the pretty_diff() method:

```python
compare.pretty_diff()
```

Example output:

```bash
Snapshot Diff for table: netflix_titles
───────────────────────────────────────────────────────
Old snapshot v1  ●  20251230_162126
New snapshot v3  ●  20251230_163729
Added columns (new → old): No added column(s)
Removed columns (new → old): listed_in, title
───────────────────────────────────────────────────────
```

You can also get the latest snapshot as a dictionary using the dict_diff() method:

```python
compare.dict_diff()

#Example output:
{'old_snapshot_version': 1,
 'old_snapshot_timestamp': '20251230_162126',
 'new_snapshot_version': 3,
 'new_snapshot_timestamp': '20251230_163729',
 'added_columns': [],
 'removed_columns': ['listed_in', 'title']}
 ```

 ### Schema Report

SchemaReport provides a consolidated overview of schema evolution for a table.

It combines snapshot metadata, timeline history, latest schema state, and snapshot differences into a single report.

It can be used:
- Audits and reviews
- Debugging schema drift
- Sharing schema change summaries
- Logging or exporting structured schema information

The SchemaReport class is built on top of SnapshotHistory and SnapshotDiff class. 

Therefore, you must first initialize a SnapshotHistory and SnapshotDiff object before you can make a full report.

```python
from detective_tools import SnapshotHistory
from detective_tools import SnapshotDiff
from detective_tools import SchemaReport

history = SnapshotHistory(table_name="netflix_titles",snapshots_dir="docs/snapshots")

compare= SnapshotDiff(history,1,3)
```

You need to create a SchemaReport object.

```python
 report= SchemaReport(history, compare)
 ```

Use pretty_report() to display a human-readable schema change report.

The main section of the report will be generated every time, further sections are optional and can be turned of by uing True or False as arguments. 

```python
report.pretty_report(main=True, add_latest=True, add_timeline=True, add_diff=True)
```
The report contains:
- General snapshot metadata
- Latest snapshot schema
- Full snapshot timeline
- Schema difference between two points if choosen

Each section is printed sequentially, making it easy to review.

Example output:

```bash
Schema Change Report for table: netflix_titles
────────────────────────────────────────────────────────────
Snapshots directory: docs/snapshots/netflix_titles
Latest snapshot version: 3 
Available versions: 1, 2, 3
Total snapshots: 3
First snapshot Created: 20251230_162126
Latest snapshot Created: 20251230_163729
────────────────────────────────────────────────────────────

 Latest Snapshot for table: netflix_titles
────────────────────────────────────────────────────────────
v3  ●  20251230_163729
    |   columns: 10
    |   rows: 8807
    |   current columns: show_id, type, director, cast, country, date_added, release_year, rating, duration, description
    | + all added columns: 
    │ - all removed columns: title, listed_in
────────────────────────────────────────────────────────────

Snapshot Timeline for table: netflix_titles
────────────────────────────────────────────────────────────

v1  ●  20251230_162126
    │ columns: 12
    │ rows: 8807
    │ initial snapshot

v2  ●  20251230_163649
    │ columns: 11
    │ rows: 8807
    │ - removed columns: title

v3  ●  20251230_163729
    │ columns: 10
    │ rows: 8807
    │ - removed columns: listed_in
────────────────────────────────────────────────────────────


Snapshot Diff for table: netflix_titles
───────────────────────────────────────────────────────
Old snapshot v1  ●  20251230_162126
New snapshot v3  ●  20251230_163729
Added columns (new → old): No added column(s)
Removed columns (new → old): listed_in, title
───────────────────────────────────────────────────────
```

You can also get the report as a dictionary using the dict_report() method.

```python
report.dict_report()

({'table_name': 'netflix_titles',
  'snapshots_directory': PosixPath('/home/bender/github/drift-detective/docs/snapshots/netflix_titles'),
  'latest_snapshot_version': 3,
  'available_versions': [1, 2, 3],
  'total_snapshots': 3,
  'first_snapshot_created': '20251230_162126',
  'latest_snapshot_created': '20251230_163729'},
 [{'version': 1,
   'timestamp': '20251230_162126',
   'column_count': 12,
   'row_count': 8807,
   'columns_added': [],
   'columns_removed': []},
  {'version': 2,
   'timestamp': '20251230_163649',
   'column_count': 11,
   'row_count': 8807,
   'columns_added': [],
   'columns_removed': ['title']},
  {'version': 3,
   'timestamp': '20251230_163729',
   'column_count': 10,
   'row_count': 8807,
   'columns_added': [],
   'columns_removed': ['listed_in']}],
 {'version': 3,
  'timestamp': '20251230_163729',
  'column_count': 10,
  'row_count': 8807,
  'current_columns': {'show_id': 'object',
   'type': 'object',
   'director': 'object',
   'cast': 'object',
   'country': 'object',
   'date_added': 'object',
   'release_year': 'int64',
   'rating': 'object',
   'duration': 'object',
   'description': 'object'},
  'all_added_columns': [],
  'all_removed_columns': ['title', 'listed_in']},
 {'old_snapshot_version': 3,
  'old_snapshot_timestamp': '20251230_163729',
  'new_snapshot_version': 1,
  'new_snapshot_timestamp': '20251230_162126',
  'added_columns': ['listed_in', 'title'],
  'removed_columns': []})
  ```
