# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/range_tree_lock_tracker.h

## Purpose
Declares the `LockTracker` implementation paired with `RangeTreeLockManager`.

## Important APIs, Types, And Functions
`RangeLockList` owns per-CF `toku::range_buffer`s and declares `Append`, `ReleaseLocks`, and `ReplaceLocks`. `RangeTreeLockTracker` implements `Track` for point and range requests, lock support flags, unsupported untrack/merge/subtract/savepoint methods, `Clear`, point status, release and replacement forwarding. `RangeTreeLockTrackerFactory` creates tracker instances.

## Control Flow
The header documents the concurrency model: append and release are transaction-owner operations, while replace can be called from other threads during lock escalation and is synchronized.

## State And Persistence Behavior
Tracker state is transient transaction memory. It may differ briefly from locktree contents because acquisition, release, and escalation are concurrent; the comments state this is harmless for current behavior.

## Dependencies And Integration Points
Depends on RocksDB lock tracker interfaces, pessimistic transaction types, mutex utilities, and Toku locktree/range_buffer. The range lock manager advertises this factory through `GetLockTrackerFactory`.

## Risks And Edge Cases
Savepoints, untracking, merging, and subtraction are unsupported, so partial unlock semantics are limited. `IsPointLockSupported()` returns false for the tracker even though the manager can reduce point locks to ranges.

## Test Signals
Factory tests should verify a range-capable tracker is created. Transaction tests should cover full clear/release behavior and unsupported operations returning no-op or not-tracked statuses.
