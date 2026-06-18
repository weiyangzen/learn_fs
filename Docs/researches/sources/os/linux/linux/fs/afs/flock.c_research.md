# File Research: sources/os/linux/linux/fs/afs/flock.c

## Purpose
Implements AFS file locking for POSIX locks and BSD `flock()` by combining VFS local lock records with AFS server-side whole-file locks.

## Main Responsibilities
- Emulates partial-file locking over the AFS3 whole-file lock model.
- Manages vnode lock state, pending and granted lock queues, lock extension, unlock deferral, and callback-based retry.
- Issues server RPCs for `SetLock`, `ExtendLock`, and `ReleaseLock`.
- Integrates VFS lock copy/release hooks so local lock records stay tied to vnode server-lock state.

## Key Functions and Data
- `afs_lock()` handles POSIX locking commands, including `GETLK`, lock, and unlock.
- `afs_flock()` maps BSD flock semantics onto the same lock engine.
- `afs_do_setlk()` is the core state machine for local/server lock acquisition.
- `afs_lock_work()` extends granted locks, releases deferred locks, and wakes pending lockers.
- `afs_next_locker()` chooses the next pending lock and handles failed lock classes.
- `afs_lock_op_done()` records server lock acquisition time and schedules extension.

## Important Details
- AFS locks expire after about five minutes; extensions are scheduled at half the wait interval.
- Partial lock behavior depends on the mount flock mode: local, OpenAFS-compatible, strict, or write-lock-for-partial.
- Server contention uses callback breaks plus periodic retries because servers do not provide a lock wait queue.
- Permission is checked locally with `afs_check_permit()` because shared local read locks may not contact the server.
- If the vnode is deleted, pending lockers are failed with `-ENOENT` and the vnode lock state becomes `AFS_VNODE_LOCK_DELETED`.
