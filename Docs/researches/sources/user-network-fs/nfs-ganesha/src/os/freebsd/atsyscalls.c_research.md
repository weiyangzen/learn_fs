<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/atsyscalls.c -->
# sources/user-network-fs/nfs-ganesha/src/os/freebsd/atsyscalls.c

## Purpose
This FreeBSD compatibility file provides wrappers for `*at` syscalls and Panasas/NFS file-handle syscalls on FreeBSD versions or kernels where libc/kernel support is incomplete.

## Important APIs, Types, and Functions
For newer FreeBSD compiler versions, it defines module-discovered wrappers `getfhat()`, `fhlink()`, and `fhreadlink()` that find syscall modules named `sys/getfhat`, `sys/fhlink`, and `sys/fhreadlink`, read their syscall numbers with `modstat()`, and invoke `syscall()`.

When `SYS_openat` is not defined, it defines hard-coded syscall numbers matching a modified FreeBSD 10.1 environment and implements wrappers for `openat`, `mkdirat`, `mknodat`, `fchownat`, `futimesat`, `fstatat`, `unlinkat`, `renameat`, `linkat`, `symlinkat`, `readlinkat`, `fchmodat`, `faccessat`, `getfhat`, `fhlink`, and `fhreadlink`.

## Control Flow
Module-discovered file-handle wrappers initialize `module_stat`, call `modfind()`, call `modstat()`, extract `stat.data.intval`, then dispatch through `syscall()`. Fallback `*at` wrappers directly call `syscall(SYS_..., args...)`.

## State and Persistence Behavior
No state is stored. Calls rely on kernel syscall/module state at runtime.

## Dependencies and Integration Points
The file depends on FreeBSD syscall headers, `sys/module.h`, `syscalls.h`, and libc `syscall()`. It supports higher-level FSAL/VFS code that expects Linux-like `*at` APIs and Ganesha-specific file-handle operations.

## Risks and Edge Cases
Returning `errno` directly on `modfind()`/`modstat()` failure is inconsistent with normal syscall wrappers that return `-1` and set `errno`. Hard-coded syscall numbers are explicitly tied to a modified FreeBSD 10.1 and are unsafe for arbitrary kernels if compiled in. The fallback only compiles when `SYS_openat` is absent, which may not align with partial syscall availability.

## Test Signals
FreeBSD build tests should cover systems with native `SYS_openat` and without it. Runtime tests need kernels/modules exposing `getfhat`, `fhlink`, and `fhreadlink`, plus basic `*at` operations through the wrappers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/atsyscalls.c -->
