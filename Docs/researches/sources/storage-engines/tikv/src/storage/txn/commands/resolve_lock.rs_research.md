# sources/storage-engines/tikv/src/storage/txn/commands/resolve_lock.rs

## Purpose
`resolve_lock.rs` implements the write phase of resolving stale or known transaction locks. It consumes a `txn_status` map from lock start timestamp to commit timestamp, plus a batch of key-lock pairs found by `ResolveLockReadPhase`, and either commits or rolls back each lock. It is used by GC and lock resolution paths after transaction status has already been determined.

## Important APIs, types, and functions
The `ResolveLock` command returns `()` and carries `HashMap<TimeStamp, TimeStamp>`, optional `scan_key`, and `Vec<(Key, Lock)>`. A zero commit timestamp means rollback; a nonzero timestamp greater than the lock timestamp means commit. `RESOLVE_LOCK_BATCH_SIZE` is 256 and is shared with the read phase. The command is marked as `is_sys_cmd`, uses `gen_lock!` on the resolved keys, and records write bytes as the encoded key sizes.

## Control flow
`process_write` creates an `MvccTxn` at timestamp zero and a zero-start `SnapshotReader`, then iterates the supplied key locks. For each lock it sets both `txn.start_ts` and `reader.start_ts` to the lock timestamp, looks up the transaction status, and dispatches to `cleanup()` for rollback or `commit()` for commit. A commit timestamp less than or equal to the lock timestamp is rejected as `InvalidTxnTso`. If `commit()` returns `TxnLockNotFound` for a pessimistic lock, the command treats it as harmless because such locks can be left behind after committed pessimistic conflict retries.

The loop stops early when `txn.write_size()` reaches `MAX_TXN_WRITE_SIZE`. In that case it records the current key as the next scan position and returns a `NextCommand` containing another `ResolveLockReadPhase`. Otherwise it returns `ProcessResult::Res`.

## State and persistence behavior
The command produces MVCC writes through `commit()` or rollback records and lock deletes through `cleanup()`. It accumulates released locks for wakeups, new acquired locks from MVCC side effects, and deduplicated `(start_ts, commit_ts)` pairs in `known_txn_status` for committed transactions. The output `WriteData` is explicitly allowed on almost-full disks because lock resolution and GC cleanup are system maintenance operations.

## Dependencies and integration points
It depends on `cleanup`, `commit`, `MvccTxn`, `SnapshotReader`, `MAX_TXN_WRITE_SIZE`, scheduler `WriteCommand`, and the paired `ResolveLockReadPhase`. It integrates with lock-manager wakeups through `ReleasedLocks`, with transaction-status caching through `known_txn_status`, and with the command scheduler by returning a follow-up read command when a batch is too large.

## Risks
The largest risk is resolving multiple shared sub-locks for the same key using a single snapshot. Since pending writes are invisible within the loop, repeated updates to one shared-lock record can overwrite each other unless lower-level shared-lock operations merge correctly. Other risks are incorrect scan continuation after write-size cutoff, missing transaction status entries due to the `expect`, and handling of stale pessimistic locks without hiding real commit errors.

## Test signals
The tests construct shared locks with multiple sub-locks on one key and validate all rollback and mixed commit/rollback results. They also verify an unresolved sibling sub-lock remains and that a final resolve unlocks the key. These tests directly target the snapshot-overwrite risk in batched shared-lock resolution.
