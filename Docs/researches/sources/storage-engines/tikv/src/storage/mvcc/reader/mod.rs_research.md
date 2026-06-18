# sources/storage-engines/tikv/src/storage/mvcc/reader/mod.rs

## Purpose

This file is the MVCC reader submodule facade. It wires together point gets, full MVCC readers, scanners, and small shared result/state types used by transaction commands to interpret write CF history.

## Important APIs, Types, and Functions

- Submodules: `point_getter`, `reader`, and `scanner`.
- Re-exports: `PointGetter`, `PointGetterBuilder`, `MvccReader`, `SnapshotReader`, `Scanner`, `ScannerBuilder`, `DeltaScanner`, `EntryScanner`, scanner utilities such as `has_data_in_range`, `near_load_data_by_write`, and `seek_for_valid_write`.
- `NewerTsCheckState` tracks whether a read path has not checked, has seen newer timestamp data, or has checked without seeing it. `PointGetter` uses it for newer-version detection and `RcCheckTs` behavior.
- `TxnCommitRecord` models the result of looking for a transaction's commit record: no record with optional overlapped write, a single matching write record, or an overlapped rollback embedded in another write.
- `OverlappedWrite` carries a write record plus GC fence for the case where another transaction's commit timestamp equals the current transaction's start timestamp.
- Convenience methods on `TxnCommitRecord` expose existence, `(commit_ts, WriteType)` info, and panic-on-wrong-variant unwrap helpers for internal/test use.

## Control Flow

The facade has little control flow of its own. It defines result shapes that `reader.rs` fills in `MvccReader::get_txn_commit_record`. Consumers can call `exist` for boolean status, `info` for command-level commit status, or unwrap helpers in code paths that have already established the expected variant.

## State and Persistence Behavior

No persistent state is owned here. The enums and structs are value types passed between reader and transaction logic. `OverlappedWrite` preserves enough write metadata to avoid overwriting an unrelated write when rolling back a transaction whose start timestamp collides with another transaction's commit timestamp.

## Dependencies and Integration Points

The module depends on `txn_types::{TimeStamp, Write, WriteType}` and integrates the concrete reader implementations with transaction status commands, cleanup/rollback logic, scanners, and tests. The `#[cfg(test)] pub use self::reader::tests as reader_tests;` export lets other MVCC tests reuse reader fixtures.

## Risks and Edge Cases

- `unwrap_*` helpers panic when called on the wrong variant, so production call sites should prefer `exist`/`info` or explicit matching unless invariants are already guaranteed.
- `TxnCommitRecord::None` can still contain `overlapped_write`; treating `None` as "safe to write rollback blindly" would be wrong.
- `OverlappedRollback` exists because rollback state can be encoded inside another transaction's write when timestamps overlap.

## Test Signals

Behavior is validated by `reader.rs` tests for normal commit lookup, pessimistic transaction ordering where commit timestamp and start timestamp order differ, overlapped writes, and overlapped rollbacks.
