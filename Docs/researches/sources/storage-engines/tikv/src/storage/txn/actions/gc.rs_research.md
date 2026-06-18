# sources/storage-engines/tikv/src/storage/txn/actions/gc.rs

## Purpose
Implements per-key MVCC garbage collection. Given a safe point, it removes obsolete write records and long default values while preserving the latest state needed to answer reads at or after the safe point.

## Important APIs, types, and functions
- `gc(txn, reader, key, safe_point) -> MvccResult<GcInfo>` is the exported action and reports `GcInfo` metrics to `STAT_TXN_KEYMODE`.
- `Gc` holds the key, current seek timestamp, info counters, `MvccTxn`, and `MvccReader`.
- `State::{Rewind, RemoveIdempotent, RemoveAll}` models the version-removal rules.
- `delete_write` deletes write CF and deletes default CF only for non-short `Put` writes.

## Control flow
`Gc::run` starts in `Rewind(safe_point)` and repeatedly `seek_write`s backward from `cur_ts`, updating `cur_ts = commit.prev()` and counting found versions. It stops and returns partial `GcInfo` if `txn.write_size >= MAX_TXN_WRITE_SIZE`.

Before the safe point, `Rewind` keeps versions. At the first version at or below safe point, it switches to `RemoveIdempotent`. This removes rollback and lock records until it sees a data state. A `Put` switches to `RemoveAll(None)` and is kept as the latest value before the safe point. A `Delete` switches to `RemoveAll(Some(delete))`, deferring deletion of that delete marker until the scan completes. Once in `RemoveAll`, every older write is deleted. If the scan completes with a deferred delete, it is also removed, allowing an all-deleted history to disappear.

## State and persistence behavior
All mutations are staged in `MvccTxn`: write CF deletes and, for long put values, default CF deletes keyed by the write start timestamp. `GcInfo` records found/deleted version counts and whether the key was fully processed. Partial completion leaves `is_completed = false`.

## Dependencies and integration points
The action depends on `MvccReader::seek_write`, `MvccTxn::delete_write/delete_value`, `MAX_TXN_WRITE_SIZE`, `txn_types::WriteType`, and GC worker metrics. Tests compare this action with compaction-filter GC behavior.

## Risks and edge cases
The state machine must keep exactly one visible value before the safe point unless a delete history can be fully removed. Removing default CF values only for long puts is essential; short values live inside write records. Partial batches must be resumable and must not mark completion. Off-by-one timestamp handling uses `commit.prev()` and `commit_ts <= safe_point`.

## Test signals
Tests build a multi-version history containing put, delete, lock, rollback, short values, and long values. They run safe points through multiple stages and verify reads before and after GC. A parallel test exercises `gc_by_compact` for the same scenarios.
