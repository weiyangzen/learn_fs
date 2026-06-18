# sources/storage-engines/tikv/src/storage/txn/actions/commit.rs

## Purpose
Implements the MVCC commit action for one key. It turns a matching prewrite lock into a write record at `commit_ts`, removes or updates the lock state, handles duplicate commits idempotently, and returns a `ReleasedLock` when the lock should be released from the lock manager. It is on TiKV's transactional write path and includes special handling for async/large transaction `min_commit_ts`, stale pessimistic locks, and shared-lock containers.

## Important APIs, types, and functions
- `commit<S: Snapshot>(txn, reader, key, commit_ts, commit_role) -> MvccResult<Option<ReleasedLock>>` is the exported action. It reads the current lock state from `MvccTxn` pending lock bytes first, then snapshot storage, writes a `Write` record, and unlocks or updates lock CF.
- `handle_lock_not_found` centralizes absent/mismatched lock behavior. It reads `reader.get_txn_commit_record(&key)?.info()`: rollback/no record becomes `TxnLockNotFound`; put/delete/lock records are treated as duplicate committed commands and return `Ok(None)`.
- `CommitRole` affects diagnostics. Secondary lock-not-found and secondary commit-ts-expired paths collect `MvccInfo` through `collect_mvcc_info_for_debug`.
- `Write::new(WriteType::from_lock_type(lock.lock_type).unwrap(), reader.start_ts, lock.short_value.take())` persists the committed version and carries `last_change` and `txn_source` from the lock.

## Control flow
The function first installs a failpoint, builds a closure that can collect debug MVCC state, and resolves the effective lock state. Pending lock bytes are preferred because batched resolve-lock can modify a shared lock and then commit another sub-lock on the same key before the batch is written. A normal lock must match `reader.start_ts`; a shared lock must contain a sub-lock with `reader.start_ts`, which is removed from the in-memory `SharedLocks` before commit processing.

If no matching lock exists, `handle_lock_not_found` distinguishes duplicate commits from real conflicts. If `commit_ts < lock.min_commit_ts`, the function returns `CommitTsExpired`, logging primary cases as expected and collecting MVCC info for secondaries or non-primary keys. Pessimistic-only locks are abnormal on commit; they are rolled back instead of committed, preserving other sub-locks when the stale pessimistic lock is inside `SharedLocks`.

For a real commit, the action builds the `Write`, marks overlapped rollback when `lock.rollback_ts` contains `commit_ts`, writes it to write CF via `txn.put_write`, and then either removes the lock (`txn.unlock_key`) or rewrites the remaining `SharedLocks`.

## State and persistence behavior
State changes are staged in `MvccTxn`: write CF receives the commit record, default CF is not touched here because prewrite wrote long values, and lock CF is deleted or rewritten. `unlock_key` returns `ReleasedLock` with commit metadata when the lock manager should observe release. Shared lock persistence is incremental: a partially committed shared-lock set remains in lock CF; the final sub-lock removal deletes lock CF. Duplicate commits increment `MVCC_DUPLICATE_CMD_COUNTER_VEC.commit` and do not mutate state.

## Dependencies and integration points
This action depends on `SnapshotReader`, `MvccTxn`, `txn_types::{Lock, SharedLocks, Write, WriteType}`, MVCC conflict/duplicate metrics, and `actions::mvcc::collect_mvcc_info_for_debug`. Command-layer commit and resolve-lock flows call this action with a transaction start timestamp already loaded in the reader.

## Risks and edge cases
The highest-risk areas are shared-lock batch visibility through pending lock bytes, preserving unrelated sub-locks when committing or rolling back one sub-lock, and correctly classifying lock-not-found as duplicate commit versus rollback/collapse. `min_commit_ts` handling is also correctness-critical for async commit and large transactions. Stale pessimistic lock rollback deliberately writes no commit record; changing that behavior would affect resolve-lock and lock-manager release semantics.

## Test signals
The module tests cover normal put/lock/delete commits, idempotent duplicate commit, lock-not-found errors, `min_commit_ts`/`CommitTsExpired`, `last_change` and `txn_source` propagation, stale pessimistic lock rollback, MVCC info collection for unexpected secondary errors, shared-lock partial commit, pending-lock-byte reads across a batch, and preservation of other shared sub-locks when a stale pessimistic sub-lock is removed.
