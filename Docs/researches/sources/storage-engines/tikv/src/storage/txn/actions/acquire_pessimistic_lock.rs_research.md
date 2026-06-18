# sources/storage-engines/tikv/src/storage/txn/actions/acquire_pessimistic_lock.rs

## Purpose
This file implements single-key pessimistic lock acquisition for TiKV transactions. It handles exclusive and shared pessimistic locks, idempotent retries, read-value and old-value return modes, not-exist constraints, conflict detection, lock-only-if-exists behavior, and the `allow_lock_with_conflict` mode that records a lock after advancing `for_update_ts` to a conflicting commit timestamp.

## Important APIs, Types, and Functions
- `acquire_pessimistic_lock` is the public action. It returns `(PessimisticLockKeyResult, OldValue)`.
- `load_old_value` chooses between already-loaded value state and `SnapshotReader::get_old_value`.
- `handle_existing_exclusive_lock` validates same-transaction exclusive pessimistic locks, updates `for_update_ts` and lock metadata, and serves duplicate/stale requests.
- `handle_existing_shared_lock` updates a same-transaction sub-lock inside `SharedLocks`.
- `ConflictInfo` converts latest-write conflicts into either a locked-with-conflict result timestamp or a `WriteConflict` error.
- `is_already_exist` recognizes constraint failures that should become write conflicts under conflict-lock mode.

## Control Flow
The action validates `lock_only_if_exists`, updates the concurrency manager max timestamp when the request implies a read, and loads the current lock. Existing exclusive locks either route to idempotent exclusive handling or block shared requests. Existing shared locks block exclusive requests unless shrink-only rules apply; shared requests may update their own sub-lock, reject shrink-only sets, or merge a new sub-lock.

If no blocking current lock exists, the action seeks the latest write. A commit newer than `for_update_ts` is either a `WriteConflict` or, when `allow_lock_with_conflict` is true, advances `for_update_ts`, marks conflict info, and forces value loading. Rollback records and overlapped rollback flags for the same start timestamp reject the lock as rolled back. The function computes `LastChange`, loads requested value/existence/old-value information, builds a `PessimisticLock`, and writes a shared or exclusive lock unless `lock_only_if_exists` suppresses locking for a missing key.

## State and Persistence Behavior
Successful acquisition writes to `CF_LOCK` through `MvccTxn`: either `Modify::PessimisticLock` for exclusive locks or a serialized `SharedLocks` `Put`. Repeated requests may update TTL, `for_update_ts`, `min_commit_ts`, `last_change`, and conflict flags. The action reads `CF_WRITE` and `CF_DEFAULT` to detect conflicts and return values.

## Dependencies and Integration Points
The action depends on `SnapshotReader`, `MvccTxn`, `check_data_constraint`, `next_last_change_info`, feature-gated `LAST_CHANGE_TS`, MVCC metrics, `PessimisticLockKeyResult`, and `txn_types` lock/value structures. It is called by pessimistic-lock commands and interacts with prewrite, cleanup, pessimistic rollback, and lock-manager wait handling.

## Risks
The branch matrix is large: exclusive versus shared, repeated versus new, conflict-allowed versus conflict-error, and value/existence/old-value combinations. `allow_lock_with_conflict` intentionally changes persisted `for_update_ts`, so stale retries must not regress it. Shared lock shrink-only behavior can block lock upgrades/downgrades. Linearizability relies on max-ts updates whenever the request reads existence or value.

## Test Signals
The test module covers normal pessimistic locking, lock/data conflicts, rollback and idempotency, return-value and lock-only-if-exists modes, GC fence visibility, old-value correctness, `should_not_exist`, existence checks, last-change computation, `allow_lock_with_conflict`, repeated requests, shared-lock creation/merge/idempotency, upgrade/downgrade blocking, and shrink-only error behavior.
