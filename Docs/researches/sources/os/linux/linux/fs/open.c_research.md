# File Research: sources/os/linux/linux/fs/open.c

Core VFS syscall and helper implementation for truncation, fallocate, access checks, directory/root changes, chmod/chown, open/openat/openat2/creat, close, and generic file open helpers. It is a central policy layer between userspace syscalls and filesystem-specific inode/file operations.

Key flows:
- `do_truncate()`, `vfs_truncate()`, `ksys_truncate()`, and `do_ftruncate()` validate regular files, write permissions, append-only state, LSM/fsnotify hooks, mount write access, leases, and idmapped mount ownership before calling `notify_change()`.
- `vfs_fallocate()` validates mutually exclusive fallocate modes, write permissions, append/immutable/swapfile restrictions, size overflow, and dispatches to `file->f_op->fallocate`.
- `do_faccessat()` implements real-credential `access()` semantics by optionally overriding fsuid/fsgid and capabilities, then performs path lookup, `noexec`, permission, and readonly checks.
- `chmod_common()` and `chown_common()` perform mount write accounting, delegation break/retry handling, LSM checks, idmapped ownership conversion, suid/sgid/capability stripping, and `notify_change()`.
- `do_dentry_open()` is the main file initialization path: binds path/inode/mapping, handles `O_PATH`, read/write accounting, file operation lookup, security/fsnotify hooks, leases, `->open()`, direct-I/O capability, readahead state, and cleanup on failure.
- `build_open_how()` and `build_open_flags()` normalize legacy and `openat2()` inputs, validate `RESOLVE_*` flags, handle `O_TMPFILE`, `O_PATH`, `O_SYNC`, `OPENAT2_REGULAR`, lookup flags, and access mode.
- `do_sys_openat2()`, `do_sys_open()`, syscall wrappers, `filp_open()`, `file_open_root()`, `vfs_open()`, `dentry_open()`, and `kernel_file_open()` provide user and in-kernel open entry points.
- `filp_flush()`, `filp_close()`, and `close()` handle filesystem flush callbacks, dnotify, POSIX lock cleanup, fd removal, and non-restartable close error normalization.
- `generic_file_open()`, `nonseekable_open()`, and `stream_open()` are exported helpers for filesystem/file-operation implementations.

Important dependencies and invariants:
- Heavy use of `mnt_idmap()`, `inode_permission()`, LSM hooks, fsnotify hooks, leases/delegations, `mnt_want_write*()`, and VFS name lookup helpers.
- Open flag validation intentionally rejects contradictory or unsafe combinations such as `O_DIRECTORY|O_CREAT`, unsupported `openat2()` flags, invalid `RESOLVE_*` combinations, and impossible `O_TMPFILE` modes.
- `do_dentry_open()` carefully unwinds path refs, fops refs, write access, and inode/file pointers on failure.
