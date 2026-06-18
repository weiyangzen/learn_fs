# sources/storage-engines/tikv/src/storage/txn/store.rs

## Purpose
`store.rs` defines read abstractions used by transaction command implementations. It provides point-get, batch-get, scan, and transaction-entry scan traits, implements them for MVCC snapshots through `SnapshotStore`, and supplies `FixtureStore` plus `FixtureStoreScanner` for deterministic tests. It also defines `TxnEntry` and `EntryBatch` for scanning raw transactional entries such as prewrite and commit records.

## Important APIs, types, and functions
`Store` exposes `get_entry`, `get`, `incremental_get_entry`, incremental statistics/newer-ts state accessors, `batch_get`, and `scanner`. `Scanner` exposes `next_entry`, `next`, `scan`, `met_newer_ts_data`, and `take_statistics`. `scan` returns per-row errors for MVCC `KeyIsLocked` while treating other errors as scan-ending failures.

`TxnEntryStore` and `TxnEntryScanner` support entry-level scans with `entry_scanner` and `scan_entries`. `TxnEntry` has `Prewrite` and `Commit` variants, stores default/write/lock KV pairs plus `OldValue`, can erase last-change metadata for comparison, can convert committed entries into user-facing key/value pairs, can derive the logical key, and can estimate encoded size. `EntryBatch` is a small capacity-bound container for transaction entries.

`SnapshotStore<S>` is the production implementation over a `Snapshot`. It stores the snapshot, read timestamp, isolation level, fill-cache flag, bypass/access lock timestamp sets, newer-ts checking flag, and an optional cached `PointGetter` for incremental gets. `FixtureStore` wraps an ordered map from `Key` to `Result<ValueEntry>`.

## Control flow
Production point gets build a fresh `PointGetter` with the current snapshot, start timestamp, isolation level, fill-cache setting, bypass locks, and access locks, then merge point-getter statistics into the caller's statistics. Incremental gets lazily build and reuse a `PointGetter` to preserve cursor locality and expose accumulated stats. Batch gets reuse one point getter across input keys and push per-key statistics after each lookup.

Production scanners first call `verify_range` to ensure requested bounds fit inside the physical snapshot bounds. They then build an MVCC `Scanner` with direction, key-only mode, cache behavior, isolation level, lock bypass/access sets, newer-ts checking, load-commit-ts behavior, and bounds. Entry scanners similarly verify bounds, translate `after_ts` into optional min/max timestamp hints, and build an MVCC entry scanner.

`FixtureStore::scanner` translates requested lower/upper bounds into `BTreeMap` range bounds, adjusts inclusivity depending on forward versus reverse scans, optionally strips values for key-only mode, clones cloneable errors through `maybe_clone`, and reverses the collected vector for descending scans. `FixtureStoreScanner::next_entry` returns entries in that prepared order.

## State and persistence behavior
This file is read-only with respect to the underlying engine. `SnapshotStore` reads MVCC state at `start_ts` and tracks only local cursor/statistics state in `point_getter_cache`. `load_commit_ts` changes whether returned `ValueEntry` includes commit timestamps and intentionally skips `access_locks` inside MVCC point-getter behavior to obtain a valid commit timestamp. `check_has_newer_ts_data` allows callers to detect whether data newer than the read timestamp was encountered.

`TxnEntry` represents persisted MVCC artifacts from the default, lock, and write column families. `erasing_last_change_ts` is a normalization helper for cases where last-change timestamps should not affect equality or output comparison.

## Dependencies and integration points
The module depends on kvproto isolation levels, `txn_types` key/value/write encodings, MVCC point getter/scanner/entry scanner builders, storage snapshot and statistics traits, and transaction error types from `mod.rs`. It is used by command action implementations for reads, scans, lock checking, MVCC introspection, flashback-like entry iteration, and tests.

## Risks and edge cases
Range verification treats an empty physical lower or upper bound as unbounded. Upper-bound verification rejects requests whose encoded upper bound is greater than the physical upper bound or empty when the physical bound is not empty. Incorrect bound handling would risk leaking keys outside a region snapshot. `TxnEntry::into_kvpair` and `to_key` are only valid for `Commit` and deliberately `unreachable!` for `Prewrite`; callers must not use them on prewrite entries.

`Scanner::scan` preserves `KeyIsLocked` as an item-level error but aborts on other errors. Fixture scanning comments note that MVCC behavior is not guaranteed after non-lock errors; tests encode that caveat. `FixtureStore::clone` requires errors to be cloneable through `maybe_clone`, so fixtures containing non-cloneable errors would panic.

## Test signals
Tests build a Rocks-backed `TestStore`, prewrite and commit deterministic keys, and assert point gets, `get_entry` commit-ts loading, batch gets, forward scans, reverse scans, bounded scans, and scanner physical-bound rejection. Fixture tests cover missing keys, embedded NUL-like raw keys, cloneable lock and bad-format errors, key-only scans, forward and reverse range behavior, and commit-ts preservation. `test_txn_entry_size` validates size accounting for prewrite/commit entries with and without old values. Benchmarks measure fixture get, batch get, scanner creation, next, and scan loops.
