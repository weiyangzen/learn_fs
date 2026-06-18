# sources/storage-engines/tikv/src/storage/txn/commands/txn_heart_beat.rs

## Purpose
`txn_heart_beat.rs` implements transaction heartbeat handling for a primary lock. A heartbeat extends the TTL of an uncommitted transaction and can piggyback a newer min-commit timestamp for non-async-commit pipelined locks.

## Important APIs, types, and functions
The `TxnHeartBeat` command carries `primary_key`, `start_ts`, `advise_ttl`, and `min_commit_ts`, and returns `TxnStatus`. It is a write command using request type `KvTxnHeartBeat`. Test helpers expose `txn_heart_beat`, `must_success`, and `must_err`.

## Control flow
`process_write` creates an `MvccTxn` and `SnapshotReader` at `start_ts`, then loads the lock for `primary_key`. If it finds a normal lock with matching timestamp, it updates TTL when `advise_ttl` is larger. It updates `min_commit_ts` only when the lock is not async commit, has positive generation, the request carries a positive min commit timestamp, and the request value is larger than the current one. If anything changed, it writes the updated lock back with `put_lock`.

If the key contains `SharedLocks` with the requested start timestamp, the command rejects it with `PrimaryMismatch`, because a shared-locked key is not a valid primary key by design. Missing or mismatched locks produce `TxnNotFound`.

## State and persistence behavior
The only persistent mutation is an updated primary lock record. Heartbeat never releases locks, so `released_locks` is empty and no waiters are woken. The response contains `TxnStatus::uncommitted(lock, false)` reflecting the final lock state. Writes are allowed on almost-full disks.

## Dependencies and integration points
It depends on `MvccTxn`, `SnapshotReader`, `TxnStatus`, `txn_types::Lock`, and shared-lock detection via `tikv_util::Either`. It integrates with lock TTL management for long-running transactions, pipelined transaction min-commit timestamp propagation, and scheduler latching for the primary key.

## Risks
The command must not accidentally mutate shared-lock records, because heartbeats are only valid for primary locks. The min-commit timestamp update is intentionally narrow; broadening it to async-commit or non-pipelined locks could violate commit timestamp rules. Another risk is returning success for the wrong transaction if only the key matches; the code guards this by checking lock timestamp.

## Test signals
Tests cover TTL extension, no-op lower TTL requests, missing locks, wrong timestamps, committed/unlocked keys, pessimistic locks, piggybacked min-commit timestamp updates, and rejection of shared-lock keys including shared locks with pipelined fields. They also verify shared-lock records remain unchanged on heartbeat errors.
