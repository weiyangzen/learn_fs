# sources/storage-engines/tikv/src/storage/txn/commands/resolve_lock_lite.rs

## Purpose
`resolve_lock_lite.rs` implements a compact lock-resolution command for a known transaction and an explicit key list. Unlike the full two-phase resolve path, it does not scan lock CF and does not batch by write size. It is intended for client-provided `resolve_keys` where the list is guaranteed to be small enough.

## Important APIs, types, and functions
The `ResolveLockLite` command carries `start_ts`, `commit_ts`, and `Vec<Key>`. It is a system write command using the `KvResolveLock` request type, latches all `resolve_keys`, and measures write bytes over those keys. A zero `commit_ts` means rollback; a nonzero `commit_ts` means commit all listed keys for `start_ts`.

## Control flow
`process_write` creates an `MvccTxn` and `SnapshotReader` at `start_ts`. It loops over `resolve_keys`, calling `commit()` with the given commit timestamp when nonzero or `cleanup()` when zero. It accumulates released locks and then builds a `WriteResult` with `ProcessResult::Res`.

## State and persistence behavior
The command persists the write records, rollback records, and lock removals produced by `commit()` or `cleanup()`. It marks the resulting write data as allowed on an almost-full disk. On commit it emits a single known transaction status tuple `(start_ts, commit_ts)`; on rollback it emits none. It does not use lock guards and always responds `OnApplied`.

## Dependencies and integration points
It depends on `MvccTxn`, `SnapshotReader`, `commit`, `cleanup`, and the scheduler write-command traits. It integrates with transaction status cache promotion via `known_txn_status`, with lock wakeups through `ReleasedLocks`, and with client-side lock resolver logic that chooses exact keys.

## Risks
The file relies on the client guarantee that `resolve_keys` is not too large. If that assumption breaks, this command can build an oversized write batch because it lacks the `MAX_TXN_WRITE_SIZE` continuation logic present in `ResolveLock`. It also assumes all keys belong to the same `start_ts`; mixed transactions will surface through lower-level MVCC errors.

## Test signals
There are no local tests in this file. Behavior is indirectly exercised by transaction lock resolver tests that use `commit()` and `cleanup()` and by any higher-level `KvResolveLock` tests that choose the lite path. Missing local tests make key-list size assumptions and shared-lock behavior important review points.
