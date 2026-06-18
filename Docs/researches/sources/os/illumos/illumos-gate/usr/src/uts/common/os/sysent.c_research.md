# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sysent.c

## Purpose

Defines the illumos system call dispatch tables and DTrace systrace wrappers. This file maps syscall numbers to kernel entry points, argument counts, return-value conventions, loadable syscall placeholders, native/compatibility ABI variants, and systrace instrumentation shims.

## Main Responsibilities

- Declare syscall implementation prototypes used by the dispatch tables.
- Define `SYSENT_*` initializer macros for syscall ABI metadata.
- Build the native `sysent[NSYSCALL]` table.
- Build the `sysent32[NSYSCALL]` table when `_SYSCALL32_IMPL` is enabled.
- Provide `nosys_ent` for unimplemented syscalls.
- Export `syscallnames` storage allocated elsewhere.
- Provide DTrace systrace entry/return wrapper functions for native and 32-bit syscalls.

## Sysent Table Model

Each `struct sysent` entry encodes:

- Argument count.
- Return-value layout flags such as `SE_64RVAL`, `SE_32RVAL1`, and `SE_32RVAL2`.
- Optional argument-structure syscall handler.
- Optional reserved field.
- C-callable function pointer or generic AP trampoline.

Important macros:

- `SYSENT_C()` for direct C-style syscalls returning 64-bit.
- `SYSENT_CI()` for direct C-style syscalls returning one 32-bit value.
- `SYSENT_2CI()` for two 32-bit return registers.
- `SYSENT_AP()` for legacy argument-structure syscalls using `syscall_ap`.
- `SYSENT_CL()` for native long-sized returns.
- `SYSENT_LOADABLE()` / `SYSENT_LOADABLE32()` for loadable syscall slots.
- `SYSENT_NOSYS()` for invalid or unsupported slots.
- `IF_LP64`, `IF_sparc`, `IF_x86`, and `IF_386_ABI` to select table entries without large `#ifdef` blocks inside the table.

## Native Syscall Coverage

The native table maps syscall numbers 0-255. Filesystem and VFS-facing entries include:

- File descriptor I/O: `read`, `write`, `readv`, `writev`, `pread`, `pwrite`, `preadv`, `pwritev`, `close`, `fcntl`, `ioctl`, `fdsync`, `sendfilev`.
- Path operations: `open`, `openat`, `unlink`, `unlinkat`, `link`, `linkat`, `rename`, `renameat`, `symlink`, `symlinkat`, `readlink`, `readlinkat`, `resolvepath`, `getcwd`.
- Metadata operations: `stat`, `lstat`, `fstat`, `fstatat`, `stat64`, `lstat64`, `fstat64`, `fstatat64`, `chmod`, `fchmod`, `fchmodat`, `chown`, `lchown`, `fchown`, `fchownat`, `mknod`, `mknodat`, `mkdir`, `mkdirat`, `rmdir`, `umask`.
- Filesystem operations: `mount`, `umount2`, `sync`, `statvfs`, `fstatvfs`, `statvfs64`, `fstatvfs64`, `statfs32`, `fstatfs32`, `sysfs`, `pathconf`, `fpathconf`, `acl`, `facl`.
- VM/file mapping operations: `mmap`, `mmapobj`, `mprotect`, `munmap`, `mincore`, `memcntl`.
- Loadable historical or subsystem slots: `nfssys`, `sharefs`, `autofssys`, `rpcsys`, `portfs`, `door`, `kaio`, and others.

## 32-bit Compatibility Table

When `_SYSCALL32_IMPL` is compiled, `sysent32` maps ILP32 processes on an LP64 kernel to ABI-specific wrappers:

- 32-bit pointer/size conversions for `read32`, `write32`, `pread32`, `pwrite32`, `readv32`, `writev32`, `readlink32`, and `readlinkat32`.
- 32-bit stat/statvfs variants such as `stat32`, `fstat32`, `lstat32`, `fstatat32`, `stat64_32`, and `statvfs64_32`.
- 32-bit STREAMS message wrappers `getmsg32`, `putmsg32`, `getpmsg32`, and `putpmsg32`.
- 32-bit signal/time/context wrappers such as `sigaction32`, `sigaltstack32`, `sigqueue32`, `stime32`, `times32`, and `waitsys32`.
- Large-file compatibility entries at syscall numbers 213-225.

## DTrace Systrace Hooks

- `systrace_stub()` is an empty probe target.
- `dtrace_systrace_syscall()` wraps native syscall execution, fires entry probes, honors `t_dtrace_stop` process stop requests, invokes the underlying syscall, converts nonzero `lwp_errno` to `-1`, and fires return probes.
- `dtrace_systrace_syscall32()` performs the same function for the 32-bit table.
- `dtrace_systrace_rtt()` fires a return-to-trap systrace return probe for the current syscall when the normal wrapper path is not used.

## Filesystem Relevance

This file is the syscall-level entry map for almost every user-visible filesystem operation. VFS, filesystem, vnode, file-descriptor, pathname, mount, ACL, stat, large-file, and memory-mapped-file behavior all become reachable through the syscall table entries defined here. It also controls ABI routing for 32-bit filesystem calls on a 64-bit kernel.

## Notable Edge Cases

- Several historical syscall numbers are preserved as loadable or `nosys` slots for ABI stability.
- LP64 kernels intentionally mark many 32-bit large-file native entries as `nosys` because the 64-bit C library maps them to native calls.
- Native syscall 0 is `nosys` on LP64 but `indir` on non-LP64.
- DTrace can request a process stop before the syscall body runs.
- Systrace return probes use different high-word casts between native and 32-bit wrappers.
