# sources/storage-engines/tikv/src/storage/txn/commands/check_secondary_locks.rs

## Purpose
Checks secondary locks for async-commit transactions. It determines whether all secondary locks still exist, whether the transaction committed, or whether it should be considered rolled back, writing protected rollbacks when needed to freeze the result.

## Important APIs, Types, and Functions
`CheckSecondaryLocks` returns `SecondaryLocksStatus`. Internal `SecondaryLockStatus` distinguishes locked, committed, and rolled-back cases. `check_determined_txn_status` reads write-CF commit records and decides whether a rollback record must be created. `check_status_from_lock` handles live locks, stale pessimistic locks, and lock release.

## Control Flow
`process_write` first updates `ConcurrencyManager` max ts to `start_ts` so a future commit cannot overwrite a protected rollback. It scans each requested key. A matching optimistic lock returns lock info. A pessimistic lock is rolled back or treated as stale after consulting write-CF. Missing locks and shared-lock cases fall back to write-CF status. The loop stops early when any key proves committed or rolled back; otherwise it accumulates lock info for all secondaries.

## State and Persistence
When status is not determined by an existing write record, the command can write a protected rollback at `start_ts`, collapse previous rollback records, and mark rollback on mismatching locks. It may unlock stale pessimistic locks and collects `ReleasedLocks`. It sets disk-almost-full allowance because resolving transaction status is progress-critical. Known committed status is returned for txn-status cache updates.

## Dependencies and Integration Points
Depends on MVCC commit-record lookup, rollback construction from `actions::check_txn_status`, resource metering for outgoing lock-info bytes, lock manager wakeup via `ReleasedLocks`, and scheduler command metrics.

## Risks and Test Signals
Correctness depends on protected rollback creation and early exit ordering. Shared locks are assumed not to be produced by async commit and are resolved through write-CF. Tests cover no-lock, committed, rollback, optimistic lock, stale pessimistic lock, overlapped rollback, and protected rollback paths.
