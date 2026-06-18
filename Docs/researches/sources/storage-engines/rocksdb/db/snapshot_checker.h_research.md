# sources/storage-engines/rocksdb/db/snapshot_checker.h

## Purpose

`snapshot_checker.h` defines the callback interface used by flush and compaction to decide whether an internal key version is visible to a snapshot, especially when transaction engines can make sequence-number visibility differ from simple sequence ordering. It provides default and write-prepared implementations plus helper predicates for GC decisions.

## Important APIs, Types, and Functions

`SnapshotCheckerResult` distinguishes `kInSnapshot`, `kNotInSnapshot`, and `kSnapshotReleased`. `SnapshotChecker::CheckInSnapshot(sequence, snapshot_sequence)` is the core virtual callback. `DisableGCSnapshotChecker` returns `kNotInSnapshot` and has a singleton `Instance`. Despite the inline comment saying this prevents values from being GCed, the intended integration depends on helper predicates that conservatively interpret checker results. `WritePreparedSnapshotChecker` delegates to a `WritePreparedTxnDB`. `DataIsDefinitelyInSnapshot` and `DataIsDefinitelyNotInSnapshot` are declared helpers for users that need conservative answers.

## Control Flow

Compaction-style callers pass a key sequence number and snapshot sequence into a checker. The checker returns a three-state answer so callers can avoid treating released snapshots as authoritative. Write-prepared transaction DBs use this hook to consult transaction commit/prepared state instead of relying only on sequence comparisons.

## State and Persistence Behavior

The base interface has no state. `DisableGCSnapshotChecker` is a process singleton. `WritePreparedSnapshotChecker` stores a raw const pointer to the owning transaction DB, so lifetime is external. The file does not persist anything, but it directly affects whether obsolete internal versions are removed during flush/compaction.

## Dependencies and Integration Points

The header depends on `rocksdb/types.h` for `SequenceNumber`. It is integrated by compaction iterators, flush garbage collection, and write-prepared transaction visibility code. The public shape intentionally avoids taking DB mutexes or ownership in the checker interface.

## Risks and Test Signals

Risks include reversed interpretation of `kInSnapshot`/`kNotInSnapshot`, use-after-free if the transaction DB outlives the checker incorrectly, and unsafe GC when the result is `kSnapshotReleased`. Tests should cover ordinary snapshots, released snapshots, write-prepared committed/uncommitted states, and compaction behavior with GC disabled.
