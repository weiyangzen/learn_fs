# sources/storage-engines/tikv/src/storage/mvcc/reader/scanner/mod.rs

## Purpose

`mod.rs` is the public assembly point for TiKV MVCC scanners. It wires forward and backward implementations into `ScannerBuilder`, defines shared scanner configuration, exposes the store-level `Scanner` enum, and provides helper functions for default-CF value loading, range probing, and old-value lookup.

The module is responsible for preserving a consistent scanner contract across normal reads, descending reads, entry scans, and delta scans. It centralizes options such as timestamp, isolation level, range bounds, fill-cache behavior, lock bypass/access sets, timestamp hints, newer-ts detection, and commit-ts loading.

## Important APIs, Types, And Functions

- `ScannerBuilder<S>` is the user-facing builder. It supports `fill_cache`, `omit_value`, `isolation_level`, `desc`, `range`, `bypass_locks`, `access_locks`, `hint_min_ts`, `hint_max_ts`, `check_has_newer_ts_data`, and `set_load_commit_ts`.
- `ScannerBuilder::build` creates either `Scanner::Forward(ForwardKvScanner)` or `Scanner::Backward(BackwardKvScanner)`.
- `build_entry_scanner(after_ts, output_delete)` creates a forward `EntryScanner` with a default-CF cursor.
- `build_delta_scanner(from_ts, extra_op)` creates a forward `DeltaScanner` with default CF in mixed scan mode.
- `build_lock_cursor` skips lock-CF cursor construction when the isolation level does not require lock checks.
- `Scanner<S>` wraps forward/backward key-value scanners and implements the storage transaction `Scanner` trait.
- `ScannerConfig<S>` stores the snapshot and all scan options. `create_cf_cursor` and `create_cf_cursor_with_scan_mode` build CF cursors with correct range, cache, scan mode, and write-CF timestamp hints.
- `near_load_data_by_write` and `near_reverse_load_data_by_write` load long values from default CF using seek hints and validate exact default keys.
- `has_data_in_range` probes for any data in a CF range and treats RocksDB "too many internal keys skipped" as evidence that data likely exists.
- `seek_for_valid_write` and `seek_for_valid_value` locate the latest value-changing write and old value while skipping locks/rollbacks and honoring GC fences and timestamp filters.
- `load_data_by_lock` reads values represented by accessible locks, including lock short values and default-CF values.

## Control Flow

Builder methods mutate `ScannerConfig`. During scanner construction, lock and write cursors are created before default cursors. This ordering matters because `ScannerConfig::create_cf_cursor_with_scan_mode` consumes `lower_bound` and `upper_bound` when building the default-CF cursor, while lock and write CFs clone them.

Normal scans call `build`, which selects backward scanning when `desc` is true and forward scanning otherwise. Entry and delta scans are always forward and require default-CF access for raw `TxnEntry` output. Delta scanning uses `ScanMode::Mixed` for the default CF.

Default-value loading constructs `user_key@start_ts`, chooses near seek or normal seek from `Statistics::load_data_hint`, and then verifies both cursor validity and exact key equality. Failure returns `default_not_found_error`, signaling storage corruption or inconsistent MVCC state.

Old-value helpers are used by delta scanning and pessimistic/prewrite paths. `seek_for_valid_write` walks write records for a user key, skipping `Lock` and `Rollback` types and checking GC fences. `seek_for_valid_value` converts a valid `Put` into an `OldValue::Value`, converts deletes or missing writes into `OldValue::None`, and returns `OldValue::SeekWrite` when write-CF timestamp filtering means the real old value may have been filtered out.

## State And Persistence Behavior

`ScannerConfig` owns the read snapshot and scan options. It does not persist state beyond cursor construction, but it deliberately consumes default-CF bounds to avoid applying the same owned range multiple times. The created scanners hold cursor state and statistics between calls.

All helper functions are read-only against the snapshot. They mutate only cursors and statistics. `has_data_in_range` performs a bounded range probe and updates the caller-supplied CF statistics.

## Dependencies And Integration Points

The module depends on TiKV engine abstractions (`Cursor`, `CursorBuilder`, `Snapshot`, `Iterator`, `ScanMode`, `LoadDataHint`, `Statistics`, `CfStatistics`), engine CF names (`CF_DEFAULT`, `CF_LOCK`, `CF_WRITE`), MVCC helpers (`NewerTsCheckState`, `default_not_found_error`), transaction traits (`StoreScanner`, `TxnEntryScanner` indirectly through forward scanners), and MVCC data types from `txn_types`.

It is the integration point between storage transaction callers and concrete scanner implementations. `ScannerBuilder` is used by tests and production MVCC readers to construct scanners with consistent isolation and range semantics. The module also re-exports `DeltaScanner`, `EntryScanner`, and `test_util` from `forward.rs`.

## Risks And Edge Cases

- Default-CF cursor construction consumes range bounds. Adding new cursor creation paths must preserve the existing order or later cursors may get incorrect bounds.
- Timestamp hints apply only to write CF. Callers must be careful using `hint_min_ts` with old-value reads because filtering can force `OldValue::SeekWrite`.
- `near_load_data_by_write` panics by contract if called with a short-value write, and returns corruption errors for missing default data.
- `has_data_in_range` intentionally treats incomplete RocksDB results as positive, which is conservative for range existence but not a precise count.
- `load_data_by_lock` assumes conflict checking already ruled out lock types that cannot be read through; lock, pessimistic, and shared variants are unreachable there.
- Scanner trait methods wrap MVCC errors into transaction-layer results, so changes here affect read API behavior across forward and backward scans.

## Test Signals

The module-level tests validate builder-level behavior across forward and backward scanners: lock and write ordering, SI lock conflicts, bypass/access locks, newer-ts detection, old-value reads with write-CF timestamp hints, RC scans skipping locks, commit-ts loading, and top lock-version behavior across `SEEK_BOUND`. These tests complement the direction-specific test modules in `forward.rs` and `backward.rs`.
