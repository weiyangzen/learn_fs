# File Research: sources/os/linux/linux-stable/fs/utimes.c

Implements VFS timestamp update syscalls and compatibility entry points: `utimensat`, older `utime`/`utimes`/`futimesat` where enabled, and 32-bit time variants. The core exported helper is `vfs_utimes()`, which validates nanosecond fields, converts `UTIME_NOW`/`UTIME_OMIT` semantics into `struct iattr`, obtains mount write access, calls `notify_change()`, and handles delegated inode retry through `break_deleg_wait()`.

Path and fd dispatch are split between `do_utimes_path()` and `do_utimes_fd()`. Path handling supports `AT_SYMLINK_NOFOLLOW` and `AT_EMPTY_PATH`, uses `filename_lookup()`, and retries stale lookups with `LOOKUP_REVAL`. File descriptor handling rejects flags and applies `vfs_utimes()` to the file path.

Compatibility code carefully rejects invalid microsecond values before converting to nanoseconds, preventing truncated invalid values from passing later validation. The file’s main correctness concerns are preserving POSIX permission semantics through `notify_change()`, not touching paths when both times are `UTIME_OMIT`, and maintaining old ABI behavior while routing all operations through one VFS timestamp path.
