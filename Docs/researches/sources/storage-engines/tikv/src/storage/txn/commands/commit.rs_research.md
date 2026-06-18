# sources/storage-engines/tikv/src/storage/txn/commands/commit.rs

## Purpose
Commits a transaction's prewritten keys by converting locks at `lock_ts` into committed write records at `commit_ts`.

## Important APIs, Types, and Functions
`Commit` contains keys, `lock_ts`, `commit_ts`, and optional `CommitRole`. `CommandExt` maps to `KvCommit`, latches all keys, and uses `commit_ts` as the command timestamp. `process_write` delegates per-key MVCC behavior to `txn::commit`.

## Control Flow
The command rejects `commit_ts <= lock_ts` with `InvalidTxnTso`. It creates an `MvccTxn` at `lock_ts`, a `SnapshotReader`, and iterates every key, calling `commit` and collecting released locks. It returns a committed `TxnStatus` result.

## State and Persistence
Successful execution writes commit records, removes locks, and may update lock-manager release data. It sets disk-almost-full allowance. `known_txn_status` records `(lock_ts, commit_ts)` for cache updates. Response is sent `OnApplied`.

## Dependencies and Integration Points
Integrates with commit-role handling for primary/secondary commit semantics, MVCC write/lock CF, lock manager waiter wakeups, and scheduler `CommitRequest` conversion in `mod.rs`.

## Risks and Test Signals
Primary risks are invalid timestamp acceptance and partial behavior across multiple keys. Test signals are mostly in shared transaction command tests and `mod.rs` test utilities, which use this command to validate prewrite/commit flows.
