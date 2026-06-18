# File Research: sources/os/bsd/freebsd-src/sys/kern/init_sysent.c

## Purpose
Generated FreeBSD native syscall switch table. It maps syscall numbers to handlers, argument counts, audit events, Capsicum capability flags, and syscall-thread accounting mode.

## Key Elements
- Header explicitly says: generated, do not edit.
- Table: `struct sysent sysent[]`.
- Argument sizing macro: `AS(name)`.
- Compatibility dispatch macros: `compat`, `compat4`, `compat6`, `compat7`, `compat10`, `compat11`, `compat12`, `compat13`, `compat14`.
- Unsupported compatibility entries fall back to `nosys`.
- Loadable or reserved subsystem placeholders use `lkmressys` / `lkmnosys`.

## Table Semantics
Each entry contains:
- `.sy_narg`: argument count in `syscallarg_t` units.
- `.sy_call`: syscall handler cast to `sy_call_t *`.
- `.sy_auevent`: audit event identifier.
- `.sy_flags`: capability-mode and related flags, commonly `SYF_CAPENABLED`.
- `.sy_thrcnt`: syscall thread accounting/static/absent state.

## Coverage
The file includes syscall numbers 0 through 602. It covers legacy BSD syscalls, modern FreeBSD syscalls, compatibility shims, jail/rctl/capsicum calls, POSIX timers, aio, kqueue, cpuset, file-handle syscalls, and newer Linux-like interfaces such as `timerfd_*`, `renameat2`, and inotify-related calls.

## Filesystem-Relevant Entries
Important VFS/filesystem-related entries include:
- `open`, `openat`, `close`, `close_range`, `read`, `write`, `readv`, `writev`, `pread`, `pwrite`, `preadv`, `pwritev`.
- `link`, `linkat`, `unlink`, `unlinkat`, `rename`, `renameat`, `renameat2`, `symlink`, `symlinkat`, `readlink`, `readlinkat`.
- `mkdir`, `mkdirat`, `rmdir`, `mkfifo`, `mkfifoat`, `mknodat`.
- `stat`, `fstat`, `lstat`, `fstatat`, `statfs`, `fstatfs`, `getfsstat`, `fhstat`, `fhstatfs`, `getdirentries`.
- `mount`, `nmount`, `unmount`, `quotactl`, `sync`, `fsync`, `fdatasync`, `fspacectl`, `copy_file_range`.

## Research Notes
This is ABI-defining generated data. Behavioral research should trace handlers in their implementation files, while syscall number, audit, and capability-mode behavior should be read from this table.
