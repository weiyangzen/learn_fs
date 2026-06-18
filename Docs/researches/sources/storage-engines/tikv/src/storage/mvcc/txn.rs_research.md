# sources/storage-engines/tikv/src/storage/mvcc/txn.rs

## Purpose
This file defines the write-side accumulator used by TiKV's MVCC transaction actions. `MvccTxn` is not an engine transaction by itself; it records the column-family mutations, pessimistic-lock metadata, memory-lock guards, and lock-wait wakeup information that higher-level actions later turn into a `WriteData` batch. It also defines `ReleasedLock`, used to notify the lock manager after commit or rollback, and `GcInfo`, used for MVCC/GC metrics.

## Important APIs, Types, and Functions
- `MAX_TXN_WRITE_SIZE` is a 32 KiB write-size threshold signal used by transaction code.
- `GcInfo::report_metrics` reports discovered and deleted MVCC version counts.
- `ReleasedLock::new` captures `start_ts`, `commit_ts`, `key`, and whether the released lock was pessimistic.
- `MvccTxn::new` initializes an empty mutation accumulator with a `ConcurrencyManager`.
- `into_modifies`, `take_guards`, and `take_new_locks` transfer accumulated engine modifications, in-memory key guards, and new lock infos to callers.
- `put_lock`, `put_pessimistic_lock`, and `put_shared_locks` write lock CF records and populate `new_locks` when a key is newly locked.
- `unlock_key` appends a lock CF delete and returns a `ReleasedLock`.
- `put_value`, `delete_value`, `put_write`, and `delete_write` encode timestamped default/write CF mutations.
- `mark_rollback_on_mismatching_lock` annotates an async-commit lock with rollback timestamps when a protected rollback would otherwise be overwritten.
- `get_pending_lock_bytes` scans pending lock CF modifications in reverse order so same-batch shared-lock cleanup can observe prior in-memory changes.

## Control Flow
Transaction actions call `MvccTxn` methods after reading a snapshot with `SnapshotReader`. The object records intent: lock CF puts/deletes, default CF value writes/deletes, and write CF records. `write_size` is incremented for mutations whose `Modify::size` is meaningful; shared-lock updates only add to size when a new shared-lock record is created. `into_modifies` asserts that `locks_for_1pc` has already been drained.

Rollback and cleanup paths use `unlock_key` to emit a lock delete and a `ReleasedLock`. Shared-lock cleanup may call `get_pending_lock_bytes` between sub-lock operations so it does not reload stale snapshot state after one sub-lock has already been removed in the same transaction batch.

## State and Persistence Behavior
Persistent state is represented as `Modify` values for `CF_LOCK`, `CF_DEFAULT`, and `CF_WRITE`. `MvccTxn` also tracks transient in-memory state: `locks_for_1pc`, `new_locks`, `guards`, and `write_size`. `clear` discards only local accumulated state, not engine state.

## Dependencies and Integration Points
The file depends on `txn_types`, `engine_traits`, `concurrency_manager`, and storage `Modify`. It is called by prewrite, commit, rollback, cleanup, check-txn-status, and pessimistic-lock acquisition. `ReleasedLock` integrates with lock-manager wakeups, while `new_locks` feeds wait-for/deadlock metadata.

## Risks
Correctness depends on callers using `is_new` accurately when writing locks. `get_pending_lock_bytes` is order-sensitive and only understands lock CF `Put`/`Delete` mutations. Protected rollback handling for async commit is subtle. `into_modifies` will panic if 1PC locks remain unprocessed.

## Test Signals
The in-file test suite covers MVCC reads, prewrite/commit/rollback, insert and not-exist constraints, write-size accounting, rollback collapse, async commit min-commit-ts behavior, timestamp overlap, GC fences, pessimistic lock amendment, shared-lock serialization, and pending shared-lock behavior.
