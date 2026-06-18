# sources/storage-engines/tikv/src/storage/txn/actions/mvcc.rs

## Purpose
Provides debug/introspection helpers for collecting all MVCC state for one key: current lock, write records, and default CF values. This is used for diagnostics and tests, not for normal transactional mutation.

## Important APIs, types, and functions
- `LockWritesVals` is `(Option<MvccLock>, Vec<(TimeStamp, Write)>, Vec<(TimeStamp, Value)>)`.
- `find_mvcc_infos_by_key(reader, key)` loads lock state, scans all write records backward, and scans default CF values for the key.
- `collect_mvcc_info_for_debug(snapshot, key)` creates an `MvccReader` and returns `None` on errors after logging.

## Control flow
The helper first calls `reader.load_lock`. Exclusive locks are returned directly. For `SharedLocks`, the first sub-lock by timestamp is returned for debug compatibility because the result type only carries one lock. It then seeks write records from `TimeStamp::max()` backward until no more writes or zero timestamp. Finally it appends all default CF values from `scan_values_in_default`.

## State and persistence behavior
Read-only. It consumes read statistics on the supplied `MvccReader` for the direct API and logs errors for the snapshot wrapper.

## Dependencies and integration points
`commit.rs` calls `collect_mvcc_info_for_debug` when unexpected secondary commit failures need richer diagnostics. Tests and debug paths use `must_find_mvcc_infos` to compare lock/write/value state.

## Risks and edge cases
This can scan unbounded MVCC history for a key; the source has a TODO to add a limit. Shared-lock reporting loses all but the first sub-lock, so it is diagnostic rather than a complete shared-lock dump. Errors are suppressed to `None` in `collect_mvcc_info_for_debug`, which is appropriate for logging paths but not for correctness decisions.

## Test signals
Tests construct a key with a live lock, two writes, and one long value in default CF. They verify the collected lock matches storage, writes are ordered by commit timestamp, short versus long value handling is correct, and `collect_mvcc_info_for_debug` returns the same tuple.
