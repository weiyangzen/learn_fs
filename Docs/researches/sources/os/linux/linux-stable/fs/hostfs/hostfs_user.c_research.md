# File Research: sources/os/linux/linux-stable/fs/hostfs/hostfs_user.c

## Purpose

Provides UML host syscall wrappers used by `hostfs_kern.c`.

## Main Entry Points

Implements all functions declared in `hostfs.h`: `stat_file`, `access_file`, `open_file`, directory iteration, pread/pwrite/lseek/fsync, creation, metadata updates, links, unlink, mkdir/rmdir/mknod, rename/renameat2, readlink, and statfs.

## Control Flow And State

The code converts host `statx` into `hostfs_stat`, including birth time when available. It returns Linux-style negative errno values. `set_attr()` applies mode, uid, gid, size, and explicit atime/mtime changes, using fd-based operations when an fd is available and path-based calls otherwise. `rename2_file()` uses `SYS_renameat2` when available, mapping `ENOSYS` or missing syscall support to `-EINVAL`.

## Dependencies

Uses libc/syscall interfaces available to UML userspace code, `os_makedev()` for device numbers, and `panic()` for impossible open modes.

## Risks

The wrappers expose host kernel behavior directly, including filesystem-specific statfs and rename semantics. Timestamp setting uses microsecond `utimes/futimes`, losing nanosecond precision. `replace_file()` returns raw `dup2()` errors without converting errno to negative values, unlike most other wrappers.
