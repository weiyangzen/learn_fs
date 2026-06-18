# File Research: sources/os/linux/linux/fs/utimes.c

## Purpose
Implements timestamp update syscalls: `utimensat`, older `utime`/`utimes`/`futimesat` variants, and 32-bit time compatibility variants. Provides the shared VFS helper `vfs_utimes()`.

## Main Functions
- `nsec_valid()`: accepts normal nanoseconds plus `UTIME_NOW` and `UTIME_OMIT`.
- `vfs_utimes()`: builds an `iattr`, obtains mount write access, calls `notify_change()`, and handles delegated inode retry.
- `do_utimes_path()`: validates pathname flags, does lookup with optional symlink following, retries stale paths with `LOOKUP_REVAL`.
- `do_utimes_fd()`: applies updates to an open fd path.
- `do_utimes()`: dispatches fd vs path operation.
- `SYSCALL_DEFINE4(utimensat)`: copies two `__kernel_timespec` values and short-circuits when both are `UTIME_OMIT`.
- Legacy syscall helpers under `__ARCH_WANT_SYS_UTIME`: `futimesat`, `utimes`, `utime`.
- Compatibility syscalls under `CONFIG_COMPAT_32BIT_TIME`: `utime32`, `utimensat_time32`, and timeval32 variants.

## Important Design Points
- `times == NULL` means touch both atime and mtime to current time with `ATTR_TOUCH`.
- Explicit timestamp arrays set `ATTR_TIMES_SET`, even when both individual timestamps are omitted or `UTIME_NOW`.
- Both `UTIME_NOW` values collapse to `times = NULL`.
- Old timeval-based APIs reject microsecond values outside `[0, 999999]`; this also rejects `UTIME_NOW`/`UTIME_OMIT`, which are only valid for `utimensat`.
- `AT_EMPTY_PATH` and `AT_SYMLINK_NOFOLLOW` are the only accepted path flags; fd mode rejects all flags.

## Cross-File Relationships
- Uses VFS permission/setattr machinery via `notify_change()`, `mnt_want_write()`, path lookup, and delegation breaking.
- Exported `vfs_utimes()` is available to other kernel code.

## Risks / Review Notes
- `UTIME_OMIT` for both timestamps must return success without path lookup, preserving POSIX/Linux ABI behavior.
- Delegation retry must drop and reacquire inode state correctly through `break_deleg_wait()`.
- Compatibility paths need careful range checking before microseconds are multiplied to nanoseconds.
