<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/linux/subr.c -->
# sources/user-network-fs/nfs-ganesha/src/os/linux/subr.c

## Purpose
This file implements Linux-specific OS abstraction routines for raw directory reads, directory entry conversion, timestamp updates, and thread/process credential changes.

## Important APIs, Types, and Functions
`vfs_readents()` invokes `syscall(SYS_getdents64, fd, buf, bcount)` and advances `*basepp` by the returned byte count. `to_vfs_dirent()` converts a raw `struct dirent64` entry into `struct vfs_dirent`. `vfs_utimesat()` wraps `utimensat()`, and `vfs_utimes()` wraps `futimens()`. `setuser()` calls `SYS_setresuid`, `setgroup()` calls `SYS_setresgid`, and `set_threadgroups()` calls `__NR_setgroups`.

## Control Flow
Directory reads return the syscall result and update base offset only on nonnegative results. Conversion copies inode, record length, type, offset, and name; it derives `d_type` from the last byte of the record. Timestamp and credential functions are thin wrappers with logging on setresuid/setresgid failure.

## State and Persistence Behavior
The functions mutate caller-provided offsets, file timestamps, and Linux credential/group state. No module-level state is stored.

## Dependencies and Integration Points
It depends on Linux syscalls, `fsal.h`, `os/subr.h`, `struct dirent64` layout, `utimensat`, `futimens`, and Ganesha logging. It is the Linux implementation selected by `src/os/CMakeLists.txt` for the `gos` object library.

## Risks and Edge Cases
The comment for `to_vfs_dirent()` mentions FreeBSD but the code is Linux-specific. Deriving `d_type` as `buf[dp->d_reclen - 1]` assumes the Linux `getdents64` record layout and ignores `bpos`; it should still point at the current record only because `dp` starts at `buf + bpos`, but the expression reads from the start of `buf`, which is suspicious unless `bpos` is zero. Credential changes use raw syscalls and log errors but do not propagate them from `setuser()`/`setgroup()`.

## Test Signals
Linux tests should verify raw directory iteration over multiple entries with nonzero `bpos`, correct file types, timestamp wrapper behavior including `UTIME_NOW`/`UTIME_OMIT`, and credential/group changes under privileged and unprivileged conditions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/linux/subr.c -->
