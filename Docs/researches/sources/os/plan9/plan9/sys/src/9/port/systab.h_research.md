# File Research: sources/os/plan9/plan9/sys/src/9/port/systab.h

Defines the syscall dispatch table and syscall-name table.

Contents:
- `typedef long Syscall(ulong*)`.
- Forward declarations for each syscall handler.
- `systab[]`: indexed by syscall numbers from `/sys/src/libc/9syscall/sys.h`, mapping to handler functions.
- `sysctab[]`: matching syscall name strings used by tracing/debug formatting.
- `nsyscall`: number of entries in `systab`.

Coverage:
- Includes current syscalls such as `Open`, `Read`, `Pread`, `Pwrite`, `Mount`, `Await`, `Tsemacquire`, `Nsec`.
- Includes deprecated/compatibility syscalls with leading underscores: `_errstr`, `_fsession`, `_fstat`, `_mount`, `_read`, `_stat`, `_write`, `_wstat`, `_fwstat`, `_wait`.

Role:
- Central portable dispatch metadata consumed by syscall entry code and `syscallfmt.c`.
