# sources/storage-engines/tikv/src/storage/txn/actions/cleanup.rs

## Purpose
This file implements cleanup of a single transaction lock by start timestamp. Cleanup removes expired or forced locks, writes rollback evidence when appropriate, reports committed transactions as errors, and supports both exclusive locks and shared-lock sub-locks.

## Important APIs, Types, and Functions
- `cleanup` is the production action. It returns an optional `ReleasedLock`.
- It first checks `MvccTxn::get_pending_lock_bytes` so batched cleanup of multiple shared sub-locks sees earlier in-batch lock mutations.
- It uses `rollback_lock` for exclusive lock rollback and `rollback_shared_lock` for shared sub-lock rollback.
- It falls back to `check_txn_status_missing_lock` when the target lock is absent or belongs to another transaction.
- Test helpers `must_succeed`, `must_err`, and `must_cleanup_with_gc_fence` exercise engine-level writes and GC-fence assertions.

## Control Flow
The function loads lock state from pending transaction mutations when available, otherwise from the snapshot. If it finds an exclusive lock for `reader.start_ts`, it checks TTL unless `current_ts` is zero. Non-expired locks return `KeyIsLocked`; expired or forced cleanup rolls the lock back. If it finds a shared-lock set containing `reader.start_ts`, it applies the same TTL rule to that sub-lock and then removes only that sub-lock.

When the target lock is absent, or the current lock state is unrelated, cleanup delegates to `check_txn_status_missing_lock` with rollback protection controlled by `protect_rollback`. A committed status becomes `ErrorInner::Committed`; an existing rollback is treated as an idempotent success; a newly missing lock returns success after rollback evidence is written if needed.

## State and Persistence Behavior
Cleanup writes through `MvccTxn`. It deletes lock CF records for exclusive locks or the last shared sub-lock, rewrites shared-lock records when other sub-locks remain, writes rollback records or overlapped rollback updates in write CF, and may delete long default CF values via `rollback_lock`. It returns `ReleasedLock` only when a lock CF key is actually released.

## Dependencies and Integration Points
It depends on `SnapshotReader`, `MvccTxn`, `check_txn_status_missing_lock`, `rollback_lock`, `rollback_shared_lock`, `TxnStatus`, MVCC metrics, and `txn_types::parse_lock` for pending lock bytes. It is used by cleanup and resolve-lock commands, and its released-lock output feeds lock-manager wakeups.

## Risks
TTL comparison uses physical time components; timestamp composition errors can cause premature or delayed cleanup. Pending lock bytes are essential for multi-sub-lock batches; ignoring them would resurrect removed shared locks from the snapshot. `protect_rollback` changes whether previous rollback records can be collapsed. Committed transactions must return errors rather than writing rollback evidence.

## Test Signals
Tests cover TTL-not-expired errors, forced and expired cleanup, cleanup of another transaction's lock, protected rollback behavior, pessimistic primary rollback protection, GC-fence helper behavior, shared pessimistic and prewrite lock cleanup, released-lock return semantics for final shared-lock removal, and pending-lock-byte handling across multiple sub-lock cleanup operations in one `MvccTxn`.
