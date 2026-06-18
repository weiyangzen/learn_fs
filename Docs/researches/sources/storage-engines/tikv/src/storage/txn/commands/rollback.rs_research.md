# sources/storage-engines/tikv/src/storage/txn/commands/rollback.rs

## Purpose
`rollback.rs` implements the transaction rollback command for a set of keys at one `start_ts`. It is the explicit cleanup counterpart to prewrite and is used when a transaction is known to have failed or must be aborted.

## Important APIs, types, and functions
The `Rollback` command carries `Vec<Key>` and `start_ts`, returns `()`, uses `KvRollback`, and latches every key. Its only execution entry point is `WriteCommand::process_write`.

## Control flow
`process_write` creates an `MvccTxn` and `SnapshotReader` at `start_ts`, then loops through all keys and calls `cleanup()` with `TimeStamp::zero()` as the current timestamp and `protect_rollback` set to `false`. The comment explains that explicit rollback is called when the transaction is known to fail, so the rollback record does not need protection. It collects released locks and returns a normal applied write result.

## State and persistence behavior
The command persists rollback records and lock removals produced by `cleanup()`. It can also remove a sub-lock from `SharedLocks`. The write data is allowed on an almost-full disk. It emits no known committed transaction status and no lock guards.

## Dependencies and integration points
It depends on `MvccTxn`, `SnapshotReader`, `cleanup`, and scheduler write-command traits. It integrates with prewrite by removing locks left by the first phase, with lock-manager wakeups through `ReleasedLocks`, and with shared-lock storage through lower-level cleanup support.

## Risks
The primary risk is preserving idempotence when rollback records already exist or when pessimistic locks and prewrite locks for the same transaction are interleaved across keys. Since rollback records are unprotected here, callers must only use this command for known-aborted transactions. Shared-lock rollback must update only the matching sub-lock and leave siblings intact.

## Test signals
Tests cover rollback when a rollback record already exists, later pessimistic prewrite on another key with the same start timestamp, and shared-lock rollback. The shared-lock test verifies one sub-lock is removed while the other remains, then the final rollback unlocks the key and stores unprotected rollback records.
