# File Research: sources/os/linux/linux/fs/locks.c

## Purpose
`locks.c` is the Linux VFS implementation of advisory file locking, open-file-description locks, BSD `flock()`, and file leases/delegations/layout leases. It provides the locking APIs used by syscalls, filesystems, NFS/lockd, and lease-breaking paths.

## Main Responsibilities
- Allocates and frees inode lock contexts, file locks, and leases.
- Maintains per-inode lists for BSD locks, POSIX/OFD locks, and leases.
- Maintains global per-CPU lock lists for `/proc/locks`.
- Maintains a global blocked-lock graph for wait queues and POSIX deadlock detection.
- Implements POSIX lock conflict detection, merging, splitting, insertion, deletion, and wait handling.
- Implements BSD flock lock handling and wait handling.
- Implements lease add/delete/break/timeout/get/set operations and notifier hooks.
- Implements syscall helpers for `flock(2)` and `fcntl(F_GETLK/F_SETLK/F_SETLKW/OFD variants)`.
- Exports VFS APIs such as `vfs_lock_file()`, `vfs_test_lock()`, `vfs_cancel_lock()`, `locks_remove_posix()`, `locks_remove_file()`, and `vfs_inode_has_locks()`.
- Implements `/proc/locks` sequence output and fd-specific lock reporting.

## Key Data Structures
- `struct file_lock_context`: per-inode lock context with `flc_lock`, `flc_flock`, `flc_posix`, and `flc_lease`.
- `file_lock_list`: per-CPU hlist used for `/proc/locks`, serialized with `file_rwsem`.
- `blocked_hash`: owner-keyed hash used to follow wait chains for deadlock detection.
- `blocked_lock_lock`: protects blocked wait graph fields (`flc_blocked_requests`, `flc_blocked_member`, `flc_blocker`) and `blocked_hash`.
- Slab caches: `file_lock_ctx`, `file_lock_cache`, and `file_lease_cache`.

## POSIX/OFD Lock Flow
`fcntl_setlk()` converts user `flock` data to `struct file_lock`, validates file mode, marks OFD ownership when needed, sets `FL_SLEEP` for blocking commands, and calls `do_lock_file_wait()`. That loops on `vfs_lock_file()` until the request is granted, denied, interrupted, or no longer deferred.

`vfs_lock_file()` delegates to a filesystem `->lock()` method if present, otherwise to `posix_lock_file()`. The core `posix_lock_inode()` path checks conflicts, handles expirable locks, performs deadlock detection for blocking POSIX locks, inserts waiters when needed, then merges/splits/replaces same-owner lock regions. Unlocking can shrink or split existing locks and wakes dependent waiters.

OFD locks reuse POSIX range machinery but use the file pointer as owner and skip process-based deadlock detection.

## BSD Flock Flow
`SYSCALL_DEFINE2(flock)` translates `LOCK_SH`, `LOCK_EX`, and `LOCK_UN`, rejects bad descriptors, initializes a whole-file `FL_FLOCK` lock, checks LSM permissions, then calls a filesystem `->flock()` method or the generic `locks_lock_file_wait()` path. Mandatory flock requests are now ignored with a once-only warning.

`flock_lock_inode()` handles replacement/removal of same-file flock locks, conflict checks against other file pointers, and optional blocking wait insertion.

## Lease Flow
Lease operations use `struct file_lease`, default lease manager operations, and `generic_setlease()`. `generic_add_lease()` checks open conflicts, inserts a lease, rechecks open conflicts after insertion to close races, and runs optional setup. `__break_lease()` constructs a synthetic breaker lease, marks conflicting leases for unlock or downgrade, calls lease-manager break callbacks, optionally waits until break completion/timeout, and disposes timed-out leases.

Lease-related helpers include `fcntl_setlease()`, `fcntl_getlease()`, delegation variants, `kernel_setlease()`, `vfs_setlease()`, notifier registration, `lease_get_mtime()`, and `inode_lease_ignore_mask()`.

## Blocked-Lock Graph
Blocked waiters are inserted under blockers using `locks_insert_block()` / `__locks_insert_block()`. Waiters can be nested under existing waiting locks when conflicts exist, forming trees. `locks_wake_up_blocks()` wakes children when a blocker changes. `locks_delete_block()` removes a waiter and wakes its dependents. POSIX deadlock detection follows owner wait chains via `blocked_hash` with a bounded iteration limit.

## Integration Points
- Lockd uses `vfs_lock_file()`, `vfs_test_lock()`, `vfs_cancel_lock()`, `locks_delete_block()`, `locks_copy_lock()`, and lock-manager callbacks.
- Filesystems can override `->lock`, `->flock`, and `->setlease`.
- Security hooks are called through `security_file_lock()`.
- `/proc/locks` uses the global lock lists and blocked graph traversal.
- NFS/NFSD and other subsystems can use lease notifiers and VFS lock exports.

## Concurrency and Lifetime Notes
- Per-inode lock state is protected by `ctx->flc_lock`.
- Global lock list changes require `file_rwsem` plus the per-CPU list spinlock and relevant `flc_lock`.
- Blocked graph mutations require `blocked_lock_lock`; some lockless checks use acquire/release ordering on `flc_blocker`.
- Lease operations combine `file_rwsem`, inode locks for delegations, and `ctx->flc_lock`.
- Close paths remove POSIX, OFD, flock, and lease state through `locks_remove_file()`.

## Risks and Edge Cases
- Lock range conversion handles negative lengths and overflow carefully; 32-bit compatibility paths can return `-EOVERFLOW`.
- `fcntl_setlk()` detects close/fcntl races by rechecking fd table identity and removes POSIX locks on mismatch.
- Filesystem asynchronous lock implementations must obey the strict `FILE_LOCK_DEFERRED` contract documented in `vfs_lock_file()`.
- `/proc/locks` output filters locks not visible in the reader's pid namespace.
- Leases may be downgraded or removed after break timeouts, with lease-manager callbacks deciding some timeout behavior.
