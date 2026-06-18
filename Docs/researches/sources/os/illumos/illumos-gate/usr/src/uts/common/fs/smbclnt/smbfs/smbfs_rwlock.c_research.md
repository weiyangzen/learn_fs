# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_rwlock.c

## Scope

This file implements the SMBFS custom reader/writer lock, borrowed from NFS, with interruptible entry and writer re-entry.

## APIs And Behavior

- `smbfs_rw_enter_sig()` enters as reader or writer. Readers wait behind active writers or waiting writers. Writers wait for active readers or owners. Current writer owner may re-enter recursively by decrementing count further.
- Interruptible waits use `cv_wait_sig()` and temporarily increment `lwp_nostop`.
- `smbfs_rw_tryenter()` attempts non-blocking reader or writer acquisition with the same recursive-writer behavior.
- `smbfs_rw_exit()` releases reader or writer ownership, unwinding recursive writer count and broadcasting when the lock becomes available.
- `smbfs_rw_lock_held()` reports whether the lock is held in reader or writer mode based on `count`.
- `smbfs_rw_init()` initializes count, waiters, owner, mutex, and condition variable.
- `smbfs_rw_destroy()` destroys synchronization primitives.

## State Model

- `count > 0` means active reader count.
- `count < 0` means writer hold depth.
- `owner` identifies the writer thread.
- `waiters` biases readers behind waiting writers to avoid writer starvation.

## Risks And Invariants

- Recursive entry is allowed only for the writer owner.
- Every recursive writer enter must be paired with an exit.
- `smbfs_rw_lock_held(RW_WRITER)` reports any writer hold, not necessarily ownership by the current thread.
