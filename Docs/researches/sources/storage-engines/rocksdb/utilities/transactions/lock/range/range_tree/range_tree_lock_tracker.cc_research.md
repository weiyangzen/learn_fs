# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/range_tree_lock_tracker.cc

## Purpose
Implements transaction-side tracking of range-tree locks so a transaction can release all Toku locktree ranges it owns.

## Important APIs, Types, And Functions
Implements `RangeTreeLockTracker::Track` for point and range requests, `GetPointLockStatus`, `Clear`, `RangeLockList::Append`, `ReleaseLocks`, and `ReplaceLocks`.

## Control Flow
Track methods serialize RocksDB point/range endpoints into DBTs and append them to a per-CF `toku::range_buffer`. `ReleaseLocks` sets `releasing_locks_` under mutex, then releases each non-empty buffer through the matching locktree, resets the buffer, retries pending lock requests, clears all buffers, and clears the releasing flag. `ReplaceLocks` is called from escalation; it skips updates during release, otherwise replaces the buffer for the escalated locktree with the locktree's new range list.

## State And Persistence Behavior
State is a map from column-family ID to `shared_ptr<toku::range_buffer>`, plus a mutex and atomic release flag. It is entirely in-memory and owned by the transaction lock tracker.

## Dependencies And Integration Points
Depends on `RangeTreeLockManager` for locktree lookup and wait callback retry, `serialize_endpoint` for DBT-compatible keys, `PessimisticTransaction`, and Toku `range_buffer` iteration.

## Risks And Edge Cases
`ReplaceLocks` assumes a buffer entry already exists for the CF and dereferences it without checking. The release path intentionally drops the mutex while walking locktrees to avoid lock-order deadlocks, relying on `releasing_locks_` to make escalation callbacks no-op. If `GetLockTreeForCF` returns null during release, the code would dereference null.

## Test Signals
Tests should observe that tracked point/range locks are released, waiting requests are retried, escalation replaces tracked ranges, and concurrent release/escalation avoids deadlock.
