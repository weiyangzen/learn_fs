# sources/storage-engines/tikv/src/storage/mvcc/reader/reader.rs

## Purpose

This file implements the general MVCC snapshot reader used by transaction commands, lock resolution, flashback reads, CDC old-value extraction, key scans, and test fixtures. It is broader than `PointGetter`: it manages cursors over all MVCC CFs, in-memory pessimistic lock table integration, transaction commit-record lookup, range scans, timestamp-filtered reads, and default CF value loading.

## Important APIs, Types, and Functions

- `SnapshotReader<S>` binds an `MvccReader<S>` to a transaction `start_ts` and exposes transaction-oriented wrappers such as `get_txn_commit_record`, `load_lock`, `key_exist`, `get`, `get_write`, `get_write_with_commit_ts`, `seek_write`, `load_data`, `get_old_value`, and `take_statistics`.
- `MvccReader<S>` stores the engine snapshot, statistics, optional CF cursors, range bounds, timestamp hints, scan mode, current key for prefix-seek reuse, fill-cache choice, region term/version, and flashback permission.
- `load_lock` checks the in-memory pessimistic-lock table first, then persisted `CF_LOCK`.
- `check_term_version_status` prevents stale in-memory lock-table reads by returning stale-command, epoch-not-match, or flashback-in-progress errors when snapshot context does not match lock table status.
- `scan_locks` merges in-memory pessimistic locks and persisted lock CF records in key order, deduplicating keys.
- `load_in_memory_pessimistic_lock_range` times read-lock hold duration with `SCAN_LOCK_READ_TIME_VEC`.
- `seek_write` finds the latest write record at or before a timestamp for a key.
- `get_write_with_commit_ts` skips `Lock`/`Rollback` records and uses `LastChange` direct-get shortcuts for long chains.
- `get_txn_commit_record` scans from `TimeStamp::max()` down to a start timestamp to handle pessimistic transaction commit-order inversions and overlapped rollback/write cases.
- `scan_locks_from_storage`, `scan_latest_user_keys`, `scan_keys`, `scan_values_in_default`, `get_old_value`, `set_range`, `set_hint_min_ts`, and `set_allow_in_flashback` support range and maintenance use cases.

## Control Flow

`SnapshotReader` delegates to `MvccReader` while supplying its transaction start timestamp as the GC fence limit for transactional reads. `MvccReader::seek_write` creates or resets a write cursor, near-seeks to `key@ts`, validates the found key belongs to the requested user key, and parses the write. `get_write_with_commit_ts` repeatedly calls `seek_write`, returning visible PUTs, treating DELETE as absence, and skipping LOCK/ROLLBACK records. When a LOCK/ROLLBACK says no prior change exists, it returns none; when `LastChange` indicates a distant prior PUT/DELETE, it does a direct `get_cf` instead of many `next` calls.

`get_txn_commit_record` scans all versions from max timestamp down because pessimistic transactions can commit out of start-ts order. It returns a matching record by `write.start_ts`, an `OverlappedRollback` if a record at `commit_ts == start_ts` carries one, or `None` with `OverlappedWrite` if another transaction's write occupies that timestamp and must not be overwritten.

`scan_locks` first reads matching in-memory locks, then storage locks, and merges the streams by key. Persisted shared locks can be filtered/truncated by individual shared-lock entries to respect limits.

## State and Persistence Behavior

The reader is read-only from the perspective of MVCC data. It reads `CF_DEFAULT`, `CF_LOCK`, and `CF_WRITE`, plus the in-memory pessimistic lock table exposed through the snapshot extension. It mutates only cursor positions, range/hint settings, statistics, and local flags. `load_data` may call `default_not_found_error` if persistent write/default CF state is inconsistent. Test fixtures in this file do write to engines, but production reader methods do not.

## Dependencies and Integration Points

The file depends on storage snapshot/cursor abstractions, `engine_traits` CF constants, `txn_types` MVCC encodings, raftstore lock-table structures, kvproto region errors, `tikv_kv::SnapshotExt` and `SEEK_BOUND`, scan-lock metrics, and MVCC transaction functions in tests. Integration points include prewrite/commit/cleanup logic, lock resolver and pessimistic rollback, flashback commands, CDC old value handling, scanner utilities, resource metering, and region snapshot bounds.

## Risks and Edge Cases

- Correctness depends on encoded-key ordering and timestamp-descending MVCC key layout.
- Prefix seek is reset when the current user key changes in non-scan mode; missing that reset could read the wrong key range.
- In-memory lock-table reads must honor term/version/flashback status or clients could receive false lock results after leader changes or region changes.
- `LastChange` shortcuts depend on accurate metadata across old versions, upgrades, rollbacks interleaved with locks, and delete records.
- Shared-lock limit handling must count individual locks, not just lock keys; tests explicitly guard this.
- `gc_fence_limit` must be supplied for transactional reads or GC-fenced historical data can be interpreted incorrectly.
- `get_txn_commit_record` must preserve overlapped writes/rollbacks to avoid corrupting another transaction's record during rollback.

## Test Signals

The extensive local test module covers timestamp table property filters, lost-delete prevention, commit-record lookup including overlapped and pessimistic ordering cases, `seek_write`, `get_write`, lock scans and shared-lock limits, latest user key scans, default data loading and missing-default errors, `get`, CDC old value extraction, prefix-seek/tombstone behavior, `LastChange` shortcuts after upgrade and across rollback interleavings, plus reusable region-engine fixtures for MVCC transaction setup.
