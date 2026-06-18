<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/subr.c -->
# sources/user-network-fs/nfs-ganesha/src/os/freebsd/subr.c

## Purpose
This file implements FreeBSD-specific OS abstraction routines for directory entry reading, generic directory entry conversion, timestamp updates, and per-thread credential changes.

## Important APIs, Types, and Functions
`vfs_readents()` wraps `getdirentries()`. `to_vfs_dirent()` converts a FreeBSD `struct dirent` in a raw buffer to `struct vfs_dirent`. `vfs_utimesat()` and `vfs_utimes()` adapt `struct timespec` arrays to FreeBSD `futimesat()`/`futimes()` timeval APIs while handling `UTIME_OMIT` and `UTIME_NOW`. Private helpers `setthreaduid()`, `setthreadgid()`, and `setthreadgroups()` discover custom syscall modules and invoke them. Public wrappers `setuser()`, `setgroup()`, and `set_threadgroups()` expose credential switching.

## Control Flow
Directory reads call the kernel and leave offset update to `getdirentries()`. Directory conversion fills inode, record length, type, offset, and name, using `d_off` when `HAS_DOFF` exists or computing offset from base/bpos/reclen otherwise. Time update wrappers return immediately for any `UTIME_OMIT`, pass `NULL` timeval arrays for any `UTIME_NOW`, or convert both timespecs to timevals. Credential helpers discover syscall numbers through `modfind()`/`modstat()` each call.

## State and Persistence Behavior
No module-level state is stored. Calls mutate kernel-visible file timestamps, directory offsets, and thread credential state.

## Dependencies and Integration Points
It depends on FreeBSD directory APIs, custom syscall modules named `sys/setthreaduid`, `sys/setthreadgid`, `sys/setthreadgroups`, Ganesha `os/subr.h`, `syscalls.h`, and logging. FSAL code uses these functions for VFS operations under caller credentials.

## Risks and Edge Cases
The `UTIME_OMIT` handling returns without changing either timestamp when either entry is omit; POSIX semantics allow updating one timestamp while omitting the other, so this loses partial updates. Similarly, any `UTIME_NOW` causes both timestamps to become current. The custom setthread syscall wrappers return `errno` on module lookup failures, while `setuser()`/`setgroup()` log `errno`; if the wrapper did not set `errno` consistently, logs can be misleading.

## Test Signals
FreeBSD tests should verify directory iteration offsets, conversion of empty inode entries, timestamp behavior for normal times, both `UTIME_OMIT`, one `UTIME_OMIT`, both `UTIME_NOW`, one `UTIME_NOW`, and credential changes with and without required syscall modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/subr.c -->
