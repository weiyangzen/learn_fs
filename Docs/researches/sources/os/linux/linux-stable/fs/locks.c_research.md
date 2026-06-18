# File Research: sources/os/linux/linux-stable/fs/locks.c

## Summary
Generic Linux file-locking core. It implements BSD `flock`, POSIX byte-range locks, open-file-description locks, file leases, delegations/layout leases, lock-manager callbacks, blocking wait trees, deadlock detection, fcntl/flock entry points, cleanup on close, and `/proc/locks`.

## Main APIs
Allocation/copy helpers include `locks_alloc_lock()`, `locks_free_lock()`, `locks_init_lock()`, `locks_copy_lock()`. Lock operations include `posix_lock_file()`, `vfs_test_lock()`, `vfs_lock_file()`, `locks_lock_inode_wait()`, `vfs_cancel_lock()`, `locks_remove_posix()`, `locks_remove_file()`, and `vfs_inode_has_locks()`. Lease APIs include `__break_lease()`, `generic_setlease()`, `vfs_setlease()`, `kernel_setlease()`, `fcntl_setlease()`, and delegation helpers.

## Behavior
Each inode lazily gets a `file_lock_context` containing FLOCK, POSIX/OFD, and lease lists. Applied locks and blocked requests form conflict trees: blockers own child waiters, and wakeups recursively re-evaluate children. POSIX locks are sorted by owner and range, then merged, split, replaced, or deleted as new requests arrive. FLOCK locks conflict by file instance. OFD locks use the file pointer as owner.

## State and Synchronization
Per-inode `flc_lock` protects lock lists. `blocked_lock_lock` protects blocked-request links, blocker pointers, and the POSIX deadlock hash. Per-CPU global lock lists plus `file_rwsem` support `/proc/locks`. Lease break state uses pending flags and timeout fields.

## Dependencies
VFS files/inodes, security hooks, file operation `->lock`, `->flock`, and `->setlease`, pid namespaces, procfs seq files, fasync signaling, sysctl, tracepoints, slabs, wait queues, RCU, and lock-manager operation vectors used by lockd/nfsd.

## Risks
The core relies on strict lock ordering and acquire/release pairing around `flc_blocker`. POSIX deadlock detection is bounded and intentionally skipped for OFD locks. Close/fcntl races are handled by rechecking the fd table and zapping POSIX locks on mismatch. Lease insertion has a required memory barrier before rechecking conflicting opens.
