# sources/storage-engines/tikv/src/storage/mvcc/reader/scanner/forward.rs

## Purpose

`forward.rs` implements TiKV's ascending MVCC scanner framework. The central `ForwardScanner<S, P>` owns the cursor loop and delegates lock/write semantics to a `ScanPolicy`. This supports normal key-value reads, latest-entry replication style reads, and delta-entry reads from the same cursor machinery.

The file exports three scanner aliases: `ForwardKvScanner<S>` for visible key-value pairs, `EntryScanner<S>` for latest `TxnEntry` records after a timestamp, and `DeltaScanner<S>` for all commits/prewrites in a timestamp interval. It also provides test builders and fixtures used by scanner tests.

## Important APIs, Types, And Functions

- `ScanPolicy<S>` defines policy-specific `Output`, `handle_lock`, `handle_write`, and `output_size`.
- `HandleRes<T>` communicates policy results back to the shared loop: return an output, skip a key while preserving a user key, or move to the next loop iteration.
- `Cursors<S>` groups optional lock cursor, write cursor, and lazy default cursor. It provides `move_write_cursor_to_next_user_key` and `ensure_default_cursor`.
- `ForwardScanner<S, P>` stores `ScannerConfig`, cursors, start flag, statistics, policy, and newer-ts state.
- `ForwardScanner::read_next` initializes lower-bound positions, merges write and lock cursors by smallest user key, handles locks first, moves the write cursor to the read timestamp, delegates write resolution, and returns policy output.
- `move_write_cursor_to_ts` skips versions newer than `cfg.ts`, records newer data, raises `RcCheckTs` write conflicts, and falls back to a direct seek after `SEEK_BOUND` next steps.
- `LatestKvPolicy` returns visible `(Key, ValueEntry)` pairs. It handles lock conflicts, `access_locks`, short values, default-CF loads, `omit_value`, `load_commit_ts`, `LastChange` shortcuts, deletes, rollbacks, and GC fences.
- `LatestEntryPolicy` returns latest `TxnEntry::Commit` records with commit timestamp greater than `after_ts`, optionally including delete writes.
- `DeltaEntryPolicy` returns prewrite and commit entries in `(from_ts, cfg.ts]`, supports shared locks, and can compute `OldValue` when `ExtraOp::ReadOldValue` is requested.
- `scan_latest_handle_lock` is a shared lock handler for latest-entry style policies.
- `TxnEntryScanner` is implemented for `ForwardScanner` policies that output `TxnEntry`.
- `test_util::EntryBuilder` and `prepare_test_data_for_check_gc_fence` construct expected transactional entries and GC-fence fixtures.

## Control Flow

On first use, `read_next` seeks write and lock cursors to the lower bound or to first keys. In each loop it forms `current_user_key` from the smaller of the write user key and lock key. The write key must be truncated from its timestamped MVCC encoding, while the lock key is already a user key. If both exist for the same key, lock processing runs before write processing.

After lock handling, if a write exists, `move_write_cursor_to_ts` advances over versions whose commit timestamp is greater than the read timestamp. Bounded `next()` calls are preferred; direct seek to `user_key@cfg.ts` is used when the version chain exceeds `SEEK_BOUND`. If the cursor still points to the same user key, the active policy resolves the write.

`LatestKvPolicy::handle_write` loops through write records until it finds a visible `Put`, sees a `Delete`, exhausts the key, or a GC fence invalidates the record. `Lock` and `Rollback` records are skipped, with `LastChange` allowing a direct seek to the last value-changing version for long lock/rollback chains.

`LatestEntryPolicy` is similar but returns raw transactional entries and stops once the key's newest relevant commit is at or below `after_ts`. It can include deletes for consumers that need delete records.

`DeltaEntryPolicy` differs by returning multiple entries per key over successive calls. It may return a lock as `TxnEntry::Prewrite`, then later return commit entries for the same key. It advances the write cursor record-by-record, skips rollback and lock write records, loads default-CF values when needed, and uses `seek_for_valid_value` to attach old values for CDC-style reads.

## State And Persistence Behavior

The scanner maintains cursor positions across calls and does not write persistent data. It reads lock/write/default CFs from the supplied snapshot. `Statistics` accumulate seek, next, processed-key, and size counters until drained. `met_newer_ts_data` is updated when locks or newer commit versions are observed.

The default cursor is optional. Entry and delta scanner builders often create it eagerly because they may need raw default entries. Normal key-value scanning creates it lazily only after a visible non-short value or readable lock requires default-CF access.

## Dependencies And Integration Points

This file depends on MVCC data types from `txn_types`, including `Key`, `WriteRef`, `WriteType`, `Lock`, `LockType`, `OldValue`, and `LastChange`; on `kvproto` `ExtraOp`, `IsolationLevel`, and `WriteConflictReason`; and on TiKV storage abstractions `Cursor`, `Snapshot`, `Statistics`, and `SEEK_BOUND`.

It integrates with `ScannerBuilder` in `mod.rs`: normal forward scans use `LatestKvPolicy`, `build_entry_scanner` uses `LatestEntryPolicy`, and `build_delta_scanner` uses `DeltaEntryPolicy`. The `TxnEntryScanner` implementation lets entry and delta scanners feed transactional scan consumers. `resource_metering::record_read_keys` and statistics connect scanner behavior to TiKV observability.

## Risks And Edge Cases

- The shared loop assumes policy methods move relevant cursors correctly. A policy that returns the wrong `HandleRes` can stall, duplicate keys, or skip data.
- `DeltaEntryPolicy` can return more than one output per user key, so its cursor movement differs from latest-value policies and is more sensitive to off-by-one timestamp bounds.
- Lock handling for `LatestKvPolicy` can read through locks only when `access_locks` allows it and `load_commit_ts` is false.
- `RcCheckTs` conflicts are raised for any newer write record observed, including comments noting possible future skipping of newer `LOCK` or `ROLLBACK` records.
- `LastChange` seek shortcuts rely on correctly maintained version metadata. Bad metadata would affect both performance and possibly which version is reached first.
- Default-CF loading treats missing long values as corruption through shared helpers.

## Test Signals

The tests cover normal latest KV scans, entry scans, and delta scans. They verify range bounds, cursor out-of-bound behavior, fallback seeking after `SEEK_BOUND`, delete output options, `after_ts` filtering, GC fences, old-value reads, shared/prewrite lock output, long value loading from default CF, RC check-ts conflicts, and `LastChange` skipping. The `test_mess` delta test builds mixed locks, puts, deletes, rollbacks, short values, and long values across multiple timestamp windows.
