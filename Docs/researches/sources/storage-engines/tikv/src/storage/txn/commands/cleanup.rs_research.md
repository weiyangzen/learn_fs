# sources/storage-engines/tikv/src/storage/txn/commands/cleanup.rs

## Purpose
Implements single-key transaction cleanup after prewrite. It rolls back a lock at `start_ts`, optionally checking TTL with `current_ts`, and protects the rollback record.

## Important APIs, Types, and Functions
`Cleanup` fields are `key`, `start_ts`, and `current_ts`. `CommandExt` reports `KvCleanup`, latches the key, and uses `start_ts` for scheduling metadata. `process_write` delegates actual rollback logic to `txn::cleanup`.

## Control Flow
Before reading MVCC state, it updates `ConcurrencyManager` max ts to `start_ts`, preventing a later commit from overwriting the protected rollback. It creates an `MvccTxn` and `SnapshotReader`, invokes `cleanup(..., protect_rollback = true)`, collects any released lock, and returns `ProcessResult::Res`.

## State and Persistence
The command may delete lock-CF state and write a protected rollback record in write-CF. It marks writes as allowed when disk is almost full, reflecting the need to complete cleanup during pressure. `ReleasedLocks` can wake pessimistic waiters. No txn-status cache entry is emitted.

## Dependencies and Integration Points
Uses shared MVCC cleanup action, `ReaderWithStats` accounting, lock manager release propagation, and the common `WriteCommand` contract. It is constructed from `CleanupRequest` in `mod.rs`.

## Risks and Test Signals
The main correctness requirement is protected rollback behavior, called out by the source comment referencing issue 7364. Regression coverage is mostly through broader MVCC cleanup/rollback tests rather than tests in this file.
