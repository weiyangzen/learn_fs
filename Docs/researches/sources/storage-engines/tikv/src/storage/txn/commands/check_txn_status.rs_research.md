# sources/storage-engines/tikv/src/storage/txn/commands/check_txn_status.rs

## Purpose
Checks a transaction primary lock and returns `TxnStatus`. It is used by lock resolution, async commit recovery, and pessimistic-lock resolution to determine whether a transaction is committed, uncommitted, expired, rolled back, or missing.

## Important APIs, Types, and Functions
`CheckTxnStatus` carries primary key, lock/start ts, caller start ts, current ts, rollback behavior, async-commit fallback flag, pessimistic-resolution mode, and primary verification. It delegates status logic to `actions::check_txn_status::{check_txn_status_lock_exists, check_txn_status_missing_lock, MissingLockAction}`. `CommandExt` exposes `KvCheckTxnStatus`, `lock_ts`, and a latch on the primary key.

## Control Flow
The command updates max ts to the maximum of `lock_ts`, non-max `current_ts`, and non-max `caller_start_ts`. It creates an `MvccTxn` at `lock_ts` and a `SnapshotReader`. If a matching normal lock exists, it runs the lock-exists action, which may push `min_commit_ts`, return uncommitted lock info, roll back expired locks, or reject primary mismatches. Shared locks on the primary are rejected as `PrimaryMismatch`. Missing or mismatched locks go through missing-lock handling, optionally writing rollback or returning an error depending on flags.

## State and Persistence
Possible writes include updated lock metadata with pushed `min_commit_ts`, protected rollback records, and lock deletion for expired locks. Released locks are returned for waiter wakeup. `WriteData` is allowed on disk-almost-full. A committed result populates `known_txn_status`; other states do not.

## Dependencies and Integration Points
Integrates with concurrency-manager request-origin checks, MVCC lock/write records, lock manager wakeup, `TxnStatusCache`, async commit fallback, and pessimistic resolving. The `verify_is_primary` flag protects corner cases where a pessimistic transaction changed its primary key.

## Risks and Test Signals
Risks center on timestamp pushing, TTL expiration using physical time, stale pessimistic primary handling, protected rollback semantics, and primary mismatch compatibility with old clients. Tests cover async-commit locks, force sync fallback, missing-lock rollback, min-commit-ts pushes, TTL expiration, resolving pessimistic locks, primary verification, overlapped rollback, and self-rollback conflicts.
