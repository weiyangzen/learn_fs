# sources/storage-engines/tikv/src/storage/txn/commands/pessimistic_rollback.rs

## Purpose
Rolls back pessimistic locks for a transaction when their `for_update_ts` is not newer than the requested rollback timestamp. It supports both explicit key lists and continuation from a scan read phase.

## Important APIs, Types, and Functions
`PessimisticRollback` carries keys, `start_ts`, `for_update_ts`, and optional `scan_key`. It returns `Vec<StorageResult<()>>`, although the explicit write phase returns an empty multi-result on completion. It works with normal locks and `SharedLocks`.

## Control Flow
For each key, it loads lock-CF state. A matching normal pessimistic lock with same start ts and `lock.for_update_ts <= self.for_update_ts` is unlocked. For shared locks, it removes only the matching pessimistic entry; if entries remain, it writes the updated shared-lock set, otherwise it unlocks the key entirely. Other locks, newer pessimistic locks, missing locks, committed records, or optimistic locks are ignored. If `scan_key` is present, it returns a `NextCommand` to continue scanning.

## State and Persistence
The command deletes lock-CF state or updates shared-lock state, collects `ReleasedLocks`, and allows writes on disk-almost-full. It does not write rollback records, preserving pessimistic rollback idempotence and allowing future transaction-status resolution to decide final status where appropriate.

## Dependencies and Integration Points
Triggered directly from `PessimisticRollbackRequest` with keys or from `PessimisticRollbackReadPhase` when keys are empty. Integrates with lock manager wakeup and MVCC shared-lock serialization.

## Risks and Test Signals
Risks include rolling back too-new locks, removing the wrong shared-lock entry, and scan continuation loops. Tests cover idempotence, missing locks, other transactions, `for_update_ts` comparisons, optimistic locks, committed transactions, and shared pessimistic lock removal.
