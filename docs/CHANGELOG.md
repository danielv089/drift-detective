# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added
- Added logging.
- Unique id generation for snapshots.
- Introduced SnapshotDataModel dataclass to represent table snapshots.
- Updated DfSnapshot to produce SnapshotDataModel instead of a plain dictionary.
- Added PsqlSnapshot class to create and manage snapshots of PostgreSQL tables.
- Added the compute_snapshot() method to support lazy evaluation.
- Added type hints.

### Changed
- SchemaVersioning has been updated and separated to dataframe and PostgreSql versioning classes to correctly detect added and removed columns for both.
- Snapshot creation logic changed to use SnapshotDataModel.

### Removed
- Removed direct dictionary-based snapshots from DfSnapshot.
- Removed direct pandas dependencies from the snapshot storage object.