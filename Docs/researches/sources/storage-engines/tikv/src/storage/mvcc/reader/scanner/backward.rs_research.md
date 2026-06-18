# sources/storage-engines/tikv/src/storage/mvcc/reader/scanner/backward.rs

## Purpose

`backward.rs` implements TiKV's descending MVCC key-value scanner, exposed as `BackwardKvScanner<S>`. It scans user keys in reverse order, merges write-CF versions with lock-CF state, applies timestamp visibility rules, and returns visible `(Key, ValueEntry)` pairs for normal transactional scans. It is selected by `ScannerBuilder::desc(true)` in `mod.rs`.

The scanner is optimized for RocksDB iterator behavior. It avoids immediate reverse seeks through a bounded `prev()` loop (`REVERSE_SEEK_BOUND`) and only falls back to seek-like operations when a key has many versions. It also lazily creates a default-CF cursor only when a visible value is not embedded as a short value in the write or lock record.

## Important APIs, Types, And Functions

- `BackwardKvScanner<S: Snapshot>` stores `ScannerConfig`, optional lock cursor, write cursor, lazy default cursor, `is_started`, `Statistics`, and `NewerTsCheckState`.
- `BackwardKvScanner::new` initializes cursors and sets `met_newer_ts_data` to `Unknown` unless newer-ts checking was enabled, in which case it starts at `NotMetYet`.
- `read_next` is the public scanner step. It initializes reverse cursor positions, repeatedly chooses the next highest user key across lock and write CFs, checks locks first, resolves a visible write version, records statistics and resource-metering, and returns one entry or end-of-scan.
- `reverse_get` resolves the visible write for one user key at `cfg.ts`. It tracks the last visible `Put`/`Delete`, detects newer committed versions, raises `RcCheckTs` conflicts, and switches between bounded reverse iteration and targeted seeks.
- `handle_last_version` converts a saved `Write` into an optional `ValueEntry`, honoring GC fence state and deletes.
- `reverse_load_data_by_write` returns an empty value for `omit_value`, a write short value when present, or lazily reads default CF with `near_reverse_load_data_by_write`.
- `move_write_cursor_to_prev_user_key` skips remaining versions for the current key using bounded `prev()` calls and then `internal_seek_for_prev` when the version chain is long.
- `ensure_default_cursor` creates the default-CF cursor using `ScannerConfig::create_cf_cursor(CF_DEFAULT)` only on demand.

## Control Flow

On the first `read_next`, the scanner positions both write and lock cursors at the upper bound with `reverse_seek`, or at the physical last key with `seek_to_last` when the scan is unbounded. Each loop iteration compares the current write user key, after stripping its MVCC timestamp, with the current lock key. Because the scan is descending, the larger user key wins. If both cursors point to the same user key, the lock is handled first.

Lock handling runs only when the configured isolation level requires lock checks. The scanner parses a lock or shared-lock payload, marks `met_newer_ts_data` when applicable, and calls `txn_types::check_ts_conflict`. A lock conflict normally becomes an MVCC error, but when `access_locks` contains the lock start timestamp and `load_commit_ts` is disabled, the scanner reads through `Put` or `Delete` locks through `load_data_by_lock`. When a lock is consumed, the lock cursor moves backward.

Write handling calls `reverse_get`. The write cursor initially points at the newest encoded write for the selected user key in descending user-key order, which is the smallest commit timestamp for that user key from the reverse iterator's perspective. `reverse_get` walks backward across encoded write keys, saving the newest visible `Put` or `Delete` found so far. If it sees a commit timestamp greater than the read timestamp, it records newer data and may throw `WriteConflictReason::RcCheckTs`. If the bounded loop cannot prove the latest visible version, it seeks to `user_key@ts` and walks forward through write records until it reaches already-checked territory.

After a write is resolved, `read_next` calls `move_write_cursor_to_prev_user_key` unless `reverse_get` already crossed into the previous user key. A returned `ValueEntry` increments write processed-key counters, processed size, and read-key metering.

## State And Persistence Behavior

The scanner itself is in-memory and does not mutate MVCC data. Its persistent effects are limited to storage-engine reads and metrics/statistics. It keeps cursor state between calls, so each `read_next` resumes where the previous call left off. `take_statistics` drains accumulated counters. `met_newer_ts_data` is sticky once it reaches `Met`; it remains `Unknown` unless explicitly enabled by the builder.

The default-CF cursor is intentionally lazy because many rows can be served from write-CF short values or filtered out by deletes, locks, and timestamp checks. When created, it consumes the builder's default-CF range bounds through `ScannerConfig`.

## Dependencies And Integration Points

This file depends on `engine_traits::CF_DEFAULT`, `kvproto` isolation and conflict reason enums, `txn_types` key/write parsing, and storage abstractions such as `Cursor`, `Snapshot`, `Statistics`, and `SEEK_BOUND`. It uses helper functions from `scanner/mod.rs`, especially `near_reverse_load_data_by_write` and `load_data_by_lock`.

It integrates with `ScannerBuilder::build` through the `Scanner::Backward` enum variant, and through the store-level `Scanner` trait implementation in `mod.rs`. It shares lock conflict semantics with point gets and forward scanning through `txn_types::check_ts_conflict` and TiKV isolation-level helpers.

## Risks And Edge Cases

- Reverse iteration relies on encoded MVCC key ordering and careful comparison between timestamped write keys and raw lock keys. Mistakes here can skip a user key or duplicate it.
- The `reverse_get` cursor can move in both directions after a targeted seek. The `last_checked_commit_ts` boundary is critical for not re-reading or missing versions.
- `RcCheckTs` currently treats newer `Lock` and `Rollback` write records as conflicts; comments note this could be refined.
- Accessing locks while `load_commit_ts` is enabled is intentionally disabled in the lock path, so callers expecting both should understand that lock read-through is bypassed.
- GC fence checks can suppress older writes even when the physical write record is present.
- Bound handling is asymmetric by direction: descending scans use the upper bound for the initial reverse seek and stop through cursor range constraints.

## Test Signals

The in-file tests cover dense version chains, rollback/delete handling, cursor movement out of bounds, fallback to `seek_for_prev`, range behavior, many RocksDB tombstones, GC fence behavior, `load_commit_ts` with top lock writes, and `RcCheckTs` conflicts. Shared tests in `mod.rs` also exercise backward scanning for locks, bypass/access locks, newer-ts detection, RC lock skipping, old value hints, and commit-ts loading.
