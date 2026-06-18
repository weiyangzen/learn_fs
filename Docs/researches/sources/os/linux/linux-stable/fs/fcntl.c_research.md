# File Research: sources/os/linux/linux-stable/fs/fcntl.c

This file implements the Linux `fcntl` and `fcntl64` syscall core, file ownership for async notifications, fasync list management, signal delivery for async I/O, descriptor flag operations, lock command dispatch, leases/delegations, pipe sizing, memfd seals, and read/write lifetime hints.

Key responsibilities:
- Implement `F_GETFD`, `F_SETFD`, `F_GETFL`, `F_SETFL`, descriptor duplication queries, and created-file queries.
- Dispatch POSIX/OFD lock commands to file-locking helpers.
- Manage `F_SETOWN`, `F_GETOWN`, `F_SETOWN_EX`, `F_GETOWN_EX`, `F_GETSIG`, and `F_SETSIG`.
- Expose owner UIDs for checkpoint/restore when configured.
- Handle leases, directory notifications, pipe size, memfd seals, write-life hints, and delegations.
- Provide native 32-bit, 64-bit, and compat syscall handling.
- Manage `fasync_struct` lists used by drivers and leases for async notification.

Important functions:
- `setfl()` validates and updates mutable file status flags: append-only restrictions, `O_NOATIME` permission, `O_NDELAY`/`O_NONBLOCK`, `O_DIRECT` capability, filesystem `check_flags`, and fasync transitions.
- `file_f_owner_allocate()` lazily allocates `struct fown_struct` with race-safe `cmpxchg`.
- `__f_setown()`, `f_setown()`, `f_delown()`, and `f_getown()` manage signal owner pid/type and credential snapshots.
- `f_setown_ex()` / `f_getown_ex()` handle typed owner selection for TID, PID, or process group.
- `rw_hint_valid()`, `fcntl_get_rw_hint()`, and `fcntl_set_rw_hint()` validate and get/set inode write lifetime hints.
- `f_dupfd_query()` reports whether another fd refers to the same `struct file`.
- `do_fcntl()` is the main command dispatcher for native fcntl.
- `check_fcntl_cmd()` allows a small safe subset for `FMODE_PATH` files.
- `SYSCALL_DEFINE3(fcntl)` and `SYSCALL_DEFINE3(fcntl64)` implement native syscall entry points.
- Compat helpers convert `compat_flock`/`compat_flock64`, fix overflow for old lock structures, and route compat syscalls through `do_compat_fcntl64()`.
- `send_sigio()` and `send_sigurg()` deliver async I/O and urgent-data signals to process, thread-group, or process-group owners after permission checks.
- `fasync_insert_entry()`, `fasync_remove_entry()`, `fasync_helper()`, and `kill_fasync()` maintain and use RCU-protected async notification lists.
- `fcntl_init()` validates open-flag bit uniqueness and creates the `fasync_cache`.

State and locking:
- `file->f_lock` protects mutable file flags during `F_SETFL` and fasync state changes.
- `fown_struct->lock` protects owner pid/type/credentials/signum.
- `fasync_lock` protects global fasync list modifications; individual entries also have `fa_lock`.
- RCU is used for pid/task lookup and fasync traversal.

Security and permission checks:
- `security_file_fcntl()` gates syscall commands.
- `inode_owner_or_capable()` gates `O_NOATIME` and write-life hint changes.
- `security_file_set_fowner()` records async owner security state.
- `security_file_send_sigiotask()` gates async signal delivery.

Failure behavior:
- Unsupported commands return `-EINVAL` from dispatch or `-ENOTTY` in lower helpers where appropriate.
- Bad fds return `-EBADF`.
- Invalid owners return `-ESRCH`; invalid signals return `-EINVAL`.
- User copy failures return `-EFAULT`.
- Compat lock results may return `-EOVERFLOW` if old ABI fields cannot represent the result.

Research relevance:
- This is the VFS syscall hub for file-descriptor control and async notification. It is not FAT-specific, but FAT file and directory operations expose `setlease` and ioctl behavior that eventually interact with this generic fcntl infrastructure.
