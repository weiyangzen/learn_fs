# File Research: sources/os/linux/linux-stable/fs/open.c

## Scope

This file implements core Linux VFS open-adjacent syscalls and helpers: `truncate`, `ftruncate`, `fallocate`, `access`, `chdir`, `chroot`, chmod/chown variants, file open construction, kernel open helpers, `open/openat/openat2/creat`, close flushing, and generic nonseekable/stream open helpers.

## Public And Internal APIs Covered

- Size and space APIs: `do_truncate()`, `vfs_truncate()`, `ksys_truncate()`, `do_ftruncate()`, `vfs_fallocate()`, `ksys_fallocate()`.
- Permission and cwd/root APIs: `do_faccessat()`, `access_override_creds()`, `chdir`, `fchdir`, `chroot`.
- Metadata APIs: `chmod_common()`, `vfs_fchmod()`, `do_fchmodat()`, `chown_common()`, `do_fchownat()`, `vfs_fchown()`.
- Open pipeline: `do_dentry_open()`, `finish_open()`, `finish_no_open()`, `vfs_open()`, `dentry_open()`, `dentry_open_nonotify()`, `kernel_file_open()`.
- Open argument handling: `build_open_how()`, `build_open_flags()`, `file_open_name()`, `filp_open()`, `file_open_root()`, `do_sys_openat2()`, `do_sys_open()`.
- Close and generic file helpers: `filp_flush()`, `filp_close()`, `close`, `vhangup`, `generic_file_open()`, `nonseekable_open()`, `stream_open()`.

## Control Flow And Behavior

- Truncation validates object type, write permission, append/lease/security/fsnotify state, write access, and mount write state before calling `notify_change()` under the inode lock.
- `fallocate` validates mutually exclusive mode bits, writable file mode, immutable/append/swapfile restrictions, overflow against `s_maxbytes`, LSM/fsnotify permissions, and delegates to `file->f_op->fallocate`.
- `access` optionally overrides subjective credentials to real uid/gid and adjusted capabilities, does path lookup, checks noexec for regular executable checks, calls `inode_permission()`, and reports read-only filesystems for write probes.
- chmod/chown operations handle idmapped mounts, delegation retry, LSM checks, privilege stripping, and `notify_change()`.
- `do_dentry_open()` sets file path, inode, mapping, write/read accounting, `f_op`, LSM and fsnotify open permissions, lease breaking, mode capabilities, readahead state, O_DIRECT support, and huge-page-cache invalidation for writers.
- `build_open_flags()` normalizes open flags, rejects invalid `openat2` resolve combinations, handles `O_PATH`, `O_TMPFILE`, `O_SYNC`, create/exclusive intent, lookup flags, and `RESOLVE_*` flags.
- `close` removes the fd before flushing, converts restart-style errors to `-EINTR`, and performs synchronous final `fput` on syscall return.

## State, Dependencies, And Invariants

- Depends on VFS path lookup, idmapped mounts, inode locking, LSM hooks, fsnotify, leases, file descriptor allocation, audit, mount write counts, and file operation tables.
- Write-access accounting balances inode, primary mount, and backing-file mount access for `FMODE_BACKING`.
- `O_PATH` files bypass normal open work and receive empty file operations plus `FMODE_PATH`.
- Open error paths must release fops, path references, write access, and reset embedded file path/inode fields exactly once.
- `openat2` performs stricter argument validation than legacy open syscalls; legacy paths pre-mask flags through `build_open_how()`.
