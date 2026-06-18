<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_storage_stats_test.go -->
# sources/sync-backup/kopia/cli/command_snapshot_storage_stats_test.go

## Purpose
Tests `snapshot ls --storage-stats` in JSON and text modes, including forward and reverse snapshot ordering.

## Important APIs, Types, And Functions
The test creates two snapshots with overlapping and new file data, parses JSON lines into `cli.SnapshotManifest`, and compares expected `snapshot.StorageStats` values. It also checks text rows for new-data/new-files/new-dirs fields.

## Control Flow
Control flow creates a repo, snapshots a directory, adds duplicate and new content, snapshots again, runs list with storage stats in normal and reverse order, and validates both per-snapshot new data and running totals.

## State And Persistence Behavior
State under test is repository content deduplication, directory object creation, snapshot manifests, and transient storage stats attached during listing.

## Dependencies And Integration Points
Integrates snapshot create, snapshot list, JSON output, storage-stat calculation, units formatting, and test JSON parsing helpers.

## Risks And Edge Cases
Expected packed byte counts are tightly coupled to repository format/packing behavior. Changes in metadata encoding can require updated expected values even when high-level behavior is intact.

## Test Signals
This is a strong regression signal for `snapshotfs.CalculateStorageStats` integration and list output, especially reverse-order semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_storage_stats_test.go -->
