# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.2.0] Unreleased

### Added 
- Introduced SnapshotDataModel dataclass to represent table snapshots.
- Updated DfSnapshot to produce SnapshotDataModel instead of a plain dictionary.

### Changed
- Snapshot creation logic changed to use SnapshotDataModel.

### Removed
- Removed direct dictionary-based snapshots from DfSnapshot.
- Removed direct pandas dependencies from the snapshot storage object.