# sources/storage-engines/tikv/src/storage/txn/actions/check_txn_status.rs

## Purpose
This file implements transaction-status resolution for primary locks and missing-lock cases. It decides whether a transaction is committed, rolled back, still locked, expired, pessimistically rolled back, or missing, and emits rollback/unlock mutations when resolution requires state changes.

## Important APIs, Types, and Functions
- `check_txn_status_lock_exists` handles a found primary lock and returns `(TxnStatus, Option<ReleasedLock>)`.
- `check_txn_status_from_pessimistic_primary_lock` handles TTL and stale forced-lock checks for pessimistic primary locks.
- `check_determined_txn_status` is a read-only lookup of existing commit/rollback records.
- `check_txn_status_missing_lock` handles absent primary locks according to `MissingLockAction`.
- `rollback_lock` removes an exclusive lock, deletes long put values when needed, writes rollback or overlapped-rollback records, and returns a release signal.
- `rollback_shared_lock` removes one sub-lock from `SharedLocks`, writes rollback records, and only deletes the lock CF key when the set becomes empty.
- `collapse_prev_rollback`, `make_rollback`, and `MissingLockAction` manage rollback-record shape and collapse behavior.

## Control Flow
For existing locks, the action validates that the lock's primary matches the requested key when requested. Invalid stale pessimistic primary locks can be unlocked and then resolved via the missing-lock path; other mismatches return `PrimaryMismatch`. Async-commit locks normally return uncommitted status without rollback or min-commit-ts pushing unless `force_sync_commit` is set.

Expired pessimistic primary locks are either pessimistically rolled back without a rollback record when resolving a pessimistic lock, or fully rolled back with a protected rollback record when resolving a prewrite lock. Expired non-pessimistic locks are rolled back. Unexpired locks may have `min_commit_ts` pushed above the caller's start timestamp and current timestamp.

Missing-lock resolution checks commit records first. Existing commit records return committed or rolled-back status. If no record exists, `MissingLockAction` decides whether to error, do nothing for resolving pessimistic locks, collapse previous rollback, mark rollback on a mismatching async lock, and write a rollback or overlapped rollback.

## State and Persistence Behavior
This file mutates `CF_LOCK`, `CF_WRITE`, and sometimes `CF_DEFAULT` through `MvccTxn`. Rollbacks delete locks, may delete long values from default CF for put locks, and either write rollback records or mark an existing overlapped write with `has_overlapped_rollback` plus optional GC fence. Min-commit-ts push rewrites the lock in lock CF.

## Dependencies and Integration Points
It depends on `SnapshotReader`, `MvccTxn`, `TxnCommitRecord`, `OverlappedWrite`, `TxnStatus`, lock types, and MVCC metrics. Cleanup and lock-resolution commands call these helpers. `MvccTxn::mark_rollback_on_mismatching_lock` is used for protected rollback evidence when another async commit lock is present.

## Risks
The panic in rollback helpers for unexpected committed records reflects a strong invariant: callers should not roll back once a non-rollback commit record exists. Primary mismatch handling has different behavior for stale pessimistic locks versus other locks. GC fence and overlapped rollback updates are consistency-critical and easy to regress.

## Test Signals
This file has no local test module, but its functions are heavily exercised by `mvcc/txn.rs`, `cleanup.rs`, and transaction command tests. Key signals include TTL expiry, async commit handling, min-commit-ts push, primary mismatch, missing-lock rollback protection, overlapped rollback flags, GC fences, shared-lock rollback, and rollback collapse.
