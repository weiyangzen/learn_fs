# File Research: sources/os/linux/linux-stable/fs/afs/flock.c

## Summary
Implements POSIX and BSD-style file locking for AFS using whole-file server locks plus local VFS lock arbitration. It supports several partial-lock emulation modes because AFS3 server locks are whole-file and cannot be upgraded or downgraded.

## Main Responsibilities
- Acquires, extends, and releases AFS/YFS server locks.
- Queues pending local lock requests and grants compatible local locks.
- Periodically renews server locks before timeout.
- Handles lock contention by waiting for callback breaks or polling.
- Integrates AFS lock state into VFS `lock` and `flock` operations.
- Cleans up vnode lock queues when VFS lock records are copied or released.

## Key APIs
- `afs_lock()`.
- `afs_flock()`.
- `afs_lock_work()`.
- `afs_lock_may_be_available()`.
- `afs_lock_op_done()`.

## Important Behavior
The lock state machine moves among `NONE`, `SETTING`, `GRANTED`, `EXTENDING`, `WAITING_FOR_CB`, `NEED_UNLOCK`, `UNLOCKING`, and `DELETED`. Successful lock RPCs record `locked_at` and schedule renewal at roughly half the AFS lock wait interval.

Partial-file locks may remain local in OpenAFS-compatible mode, always use a server lock in strict mode, or force an exclusive server lock in write mode. After a server lock is obtained, VFS locking still decides local access among processes on the same client.

If the server reports contention, blocking callers wait on the file lock waitqueue. Because servers may not notify on lock expiry, the client schedules periodic retry work.

## State and Synchronization
`vnode->lock` protects pending/granted lock lists, lock key, lock type, and lock state. Server unlock can be deferred to the `afs_lock_manager` workqueue so signal-interruptible contexts do not interrupt rxrpc release. VFS lock-copy/release callbacks keep AFS vnode queues aligned with copied kernel lock records.

## Risks
The implementation must reconcile three views of locking: server whole-file lock state, local VFS byte-range state, and AFS callback notifications. Interruptions after dispatching a lock RPC can leave ambiguous server state until timeout or cleanup. Starvation is possible because local compatible locks can be granted while other clients wait.
