
# sources/sync-backup/kopia/tests/robustness/checker/checker.go

## Purpose
Defines a robustness checker that wraps snapshot creation, restore verification, deletion, and metadata reconciliation for long-running robustness tests.

## Important APIs, Types, And Functions
- `Checker` holds restore directory, `robustness.Snapshotter`, metadata `Store`, recovery mode flag, delete limit, mutex, and `SnapIDIndex`.
- `NewChecker` creates a temp restore directory and reads `LIVE_SNAP_DELETE_LIMIT`.
- `SnapshotMetadata` stores snapshot ID, start/end times, deletion time, and validation fingerprint.
- `VerifySnapshotMetadata` reconciles live snapshot metadata with live snapshots in the repository and optionally repairs in recovery mode.
- `TakeSnapshot` creates a snapshot and saves validation metadata.
- `RestoreSnapshot`, `RestoreSnapshotToPath`, `safeRestorePrepare`, and `RestoreVerifySnapshot` restore and compare data or recover missing metadata.
- `DeleteSnapshot`, `safeDeletePrepare`, and `safeDeleteFinish` mark snapshots deleted while avoiding races with restores.
- `saveSnapshotMetadata` and `loadSnapshotMetadata` persist JSON metadata by snapshot ID.

## Control Flow
Snapshot operations use the snapshotter to create/restore/delete repository snapshots and update metadata indexes under mutexes. Restore prepares by confirming a snapshot is still live, then compares restored data against saved validation fingerprints. Delete removes IDs from the live index before calling repository delete, then records deletion metadata.

## State And Persistence Behavior
Persists snapshot metadata JSON through `robustness.Store`, maintains in-memory `SnapIDIndex` categories for all/live/deleted snapshots, and creates temporary restore directories. In recovery mode it can delete live repository snapshots with missing metadata or rebuild metadata from restored data.

## Dependencies And Integration Points
Uses `robustness.Snapshotter`, `robustness.Store`, `snapmeta.Index`, `internal/clock`, and JSON metadata.

## Risks And Edge Cases
`VerifySnapshotMetadata` is documented as not concurrently safe despite using some locks; external callers must serialize it. Recovery mode deletes repository snapshots without metadata up to `DeleteLimit`, so misconfigured metadata can cause data loss in a test repo. `NewChecker` logs default delete limit if env var is unset or unparsable.

## Test Signals
Core correctness layer for robustness tests, checking snapshot metadata/data integrity and recovery semantics.
