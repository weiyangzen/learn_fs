# sources/object-store/rustfs/crates/lock/src/distributed_lock.rs

## Purpose
Implements quorum-based distributed locking over multiple `LockClient`s, returning RAII guards that release all underlying client locks asynchronously.

## Important APIs, Types, And Functions
`DistributedLockGuard` holds the public aggregate lock id, underlying `(LockId, client)` entries, lock type, and disarm state. It exposes `lock_id`, `disarm`, `is_disarmed`, and `release`; `Drop` calls release. `DistributedLock` stores clients, namespace, and write quorum. Public methods include `new`, `namespace`, `get_resource_key`, `lock_guard`, `lock_guard_quiet`, and `rlock_guard`; internal methods implement quorum acquisition, retry, cleanup, and failure classification.

## Control Flow
Acquisition clones a request to all clients in a `JoinSet`. For distributed attempts, each retry uses a fresh lock id and a bounded per-attempt timeout. Success is reached when individual successful locks meet the required quorum: configured quorum for exclusive locks and majority-like read quorum for shared locks. The returned lock id is an aggregate id, while the guard stores real per-client lock ids for release.

Failures are classified as retryable contention, non-retryable, or unrecoverable quorum. Partial successes are rolled back by background release cleanup. Pending late successes are also cleaned up asynchronously to avoid leaked locks. If hard RPC failures make quorum impossible, acquisition returns `LockError::QuorumNotReached`; contention/timeouts normally return `Ok(None)`.

## State And Persistence
No persistent state. Runtime state includes outstanding per-client lock entries owned by `DistributedLockGuard`. Drop/release spawns asynchronous cleanup with retries and metric decrement.

## Dependencies And Integration
Uses `LockClient`, generic lock DTOs, `LockError`, `futures::join_all`, Tokio `JoinSet`, `uuid`, tracing, and `rustfs_io_metrics` lock-held counters. It is the distributed coordination layer above local or remote lock clients.

## Risks And Edge Cases
Cleanup is best-effort and asynchronous; after all retry attempts, unreleased entries are only logged. If dropped outside an active Tokio runtime, it creates a current-thread runtime in a spawned OS thread, which is pragmatic but can hide cleanup latency. Failure classification depends on string prefixes for remote RPC failures and timeouts, so remote clients must preserve those message contracts. Read quorum differs from configured write quorum and should be reviewed against consistency requirements.

## Test Signals
Extensive tests cover remote RPC failure classification, warning policy, quorum impossible errors, retrying remote timeouts and transient timeouts, bounded per-attempt timeouts, clients ignoring budget, partial quorum rollback and retry with fresh lock ids, preserving non-retryable failures, and late-success cleanup so only retry-attempt locks remain active.
