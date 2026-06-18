# sources/storage-engines/tikv/src/storage/mvcc/reader/point_getter.rs

## Purpose

This file implements the optimized MVCC point-read path. `PointGetter` reads a single user key at a timestamp, checks lock conflicts when required, skips rollback/lock write records, honors GC fences, optionally reports newer timestamp data, supports read-through of selected locks, and gathers storage statistics.

## Important APIs, Types, and Functions

- `PointGetterBuilder<S: Snapshot>` configures snapshot, cache filling, value omission, isolation level, read timestamp, bypass/access lock sets, and newer-ts checking.
- `PointGetter<S>` stores the snapshot, read options, `NewerTsCheckState`, accumulated `Statistics`, and a prefix-seek write cursor over `CF_WRITE`.
- `get` returns `Option<Value>` for a user key.
- `get_entry` returns `Option<ValueEntry>` and can load the visible commit timestamp when requested.
- `load_and_check_lock` uses `snapshot.get_cf(CF_LOCK, user_key)` for the common no-lock fast path, parses single/shared lock encodings, applies `txn_types::check_ts_conflict`, supports bypass locks, and can return an accessible committed lock for read-through.
- `load_data` seeks write CF to the visible version, handles newer-ts/RcCheckTs probing, skips rollbacks and locks, uses `LastChange` shortcuts when many lock records sit above the last PUT/DELETE, checks GC fences, and loads short/default values.
- `load_data_from_default_cf` performs direct `get_cf(CF_DEFAULT)` and raises `default_not_found_error` if a referenced default value is missing.
- `load_data_from_lock` reads a value directly from an accessible committed lock when the lock's value is visible but not committed in write CF yet.

## Control Flow

`get_entry` first checks locks under SI or `RcCheckTs`. If a conflict lock is in `access_locks` and commit timestamp is not requested, it reads through the lock. Otherwise it calls `load_data`. `load_data` optionally first seeks to `user_key@TimeStamp::max()` to detect newer committed data or implement `RcCheckTs`; for `RcCheckTs`, a newer commit timestamp produces a write-conflict error. It then seeks or near-seeks to `user_key@read_ts`, parses the write record, and loops until it finds a visible `Put`, a `Delete`, an absence marker, or exhaustion. `Lock` and `Rollback` writes may terminate early via `LastChange::NotExist`, jump by direct `get_cf` when `estimated_versions_to_last_change >= SEEK_BOUND`, or continue to the next write record.

## State and Persistence Behavior

The getter is read-only. It uses a snapshot and CF cursors, mutating only in-memory cursor position, statistics, and newer-ts state. It reads `CF_LOCK`, `CF_WRITE`, and `CF_DEFAULT`. It records read-key resource metering for visible puts and updates processed size for returned values.

## Dependencies and Integration Points

Dependencies include storage `Snapshot`, `CursorBuilder`, `Statistics`, `ScanMode`, `txn_types` key/write/lock structures, `TsSet`, `LastChange`, `tikv_kv::SEEK_BOUND`, isolation-level helpers, resource metering, and MVCC errors. It is the likely read path for batch/point get commands that do not require full scanner behavior.

## Risks and Edge Cases

- Prefix seek is safe only because the cursor is built with prefix seeking and callers use encoded `Key`; changing cursor semantics would require explicit user-key checks.
- `load_commit_ts = true` deliberately ignores `access_locks`, because lock records do not have a final commit timestamp.
- `RcCheckTs` currently treats any newer write record as conflict, with a TODO noting that newer `LOCK` or `ROLLBACK` write types might be skippable.
- Missing default CF data triggers critical error behavior and may panic under config.
- `LastChange` shortcut correctness depends on transaction write records preserving accurate last-change metadata, especially across upgrades and GC fences.
- Shared-lock parsing is delegated to `txn_types::check_ts_conflict`; conflict extraction assumes error results for single locks.

## Test Signals

Tests cover basic timestamp visibility, prefix seek isolation from neighboring keys, tombstone behavior, iterator lower bounds, lock conflicts, omitted values, latest-value semantics, bypass/access locks, newer-ts detection, GC fence filtering, `RcCheckTs`, skipping lock-only histories with `LastChange`, row checksum preservation, commit timestamp loading, and shortcut behavior above PUT and DELETE records with both below- and above-`SEEK_BOUND` lock chains.
