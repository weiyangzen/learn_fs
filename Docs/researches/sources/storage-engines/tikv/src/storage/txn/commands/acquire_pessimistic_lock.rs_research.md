# sources/storage-engines/tikv/src/storage/txn/commands/acquire_pessimistic_lock.rs

## Purpose
Implements the command-layer wrapper for acquiring pessimistic locks on one or more keys. It converts request fields into action calls, handles lock-wait/resumable results, returns optional old/current values, stages writes, and reports newly acquired locks to the scheduler.

## Important APIs, types, and functions
- The `command!` macro defines `AcquirePessimisticLock` fields: keys `(Key, should_not_exist, is_shared_lock)`, primary, `start_ts`, TTL, first-lock flag, `for_update_ts`, wait timeout, return-values flag, `min_commit_ts`, existence flags, and `allow_lock_with_conflict`.
- `CommandExt` supplies context, request tag/type, timestamp, write byte accounting, pipelining, and lock key extraction.
- `WriteCommand::process_write` is the execution entry point.
- `make_write_data(modifies, old_values)` attaches `TxnExtra { old_values, one_pc: false, allowed_in_flashback: false }` when writes exist.

## Control flow
`process_write` rejects multi-key requests when `allow_lock_with_conflict` is enabled. It creates `MvccTxn` and `ReaderWithStats<SnapshotReader>`, then iterates keys. Each key calls `txn::acquire_pessimistic_lock` with request flags including existence checks, old-value requirement, lock-only-if-exists, conflict allowance, and shared-lock mode.

Successful keys push a `PessimisticLockKeyResult` and, when available, insert old values. `KeyIsLocked` builds `PessimisticLockParameters` and `WriteResultLockInfo`, clears prior mutations/results, marks the response as `Waiting`, and stops. `NotInShrinkMode` marks existing shared locks shrink-only, clears previous mutations/results/old values, writes the updated shared lock, and returns a `KeyIsLocked`-style error for the shared lock. Other MVCC errors are returned directly.

After the loop, the command extracts new locks and modifies. If an encountered lock has no wait timeout, legacy requests return a command error while resumable `allow_lock_with_conflict` requests store a per-key `Failed` result. The final `WriteResult` uses `ResponsePolicy::OnProposed`, includes lock-wait info, staged `WriteData`, rows, process result, and no released locks.

## State and persistence behavior
The command itself stages, but does not apply, lock CF modifications in `WriteData`. It may also stage a shrink-only update to an existing `SharedLocks` value. `TxnExtra.old_values` carries resolved old values for CDC/extra-op consumers. `new_acquired_locks` are taken from `MvccTxn` for lock manager bookkeeping.

## Dependencies and integration points
This command depends on the lower-level `txn::acquire_pessimistic_lock` action, `LockManager` wait semantics, `ReaderWithStats`, `WriteContext`, `PessimisticLockResults`, `PessimisticLockParameters`, resource metering, and `TxnStatusCache` in tests. It is the command executed by scheduler/write workers for TiDB pessimistic locking.

## Risks and edge cases
Clearing prior successful locks on the first wait/error is deliberate; otherwise a partially successful multi-key request could persist locks before waiting. The protocol split for `allow_lock_with_conflict` is subtle: only single-key requests are supported and errors become per-key failures. Shared lock shrink-only conversion must be persisted even though the command returns a lock error. Old values must be cleared if mutations are cleared to avoid reporting values for unapplied locks.

## Test signals
Tests cover return-values across put/delete/lock/rollback histories, per-key equality for `PessimisticLockKeyResult`, shared lock acquisition by multiple transactions, exclusive lock conversion to shrink-only, subsequent wait behavior for exclusive and shared requests, and helper execution through a full `WriteContext`.
