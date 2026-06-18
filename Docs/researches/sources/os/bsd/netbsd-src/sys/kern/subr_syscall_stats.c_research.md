# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_syscall_stats.c

Read completely: 78 lines.

This file defines optional global syscall statistics arrays and exposes them through sysctl when `SYSCALL_STATS` is compiled in.

Data:
- `syscall_counts[SYS_NSYSENT]` counts per-syscall invocations.
- `syscall_count_user`, `syscall_count_system`, and `syscall_count_interrupt` count syscall context categories.
- `syscall_times[SYS_NSYSENT]` is present only with `SYSCALL_TIMES`.

`SYSCTL_SETUP(sysctl_syscall_setup)` creates `kern.syscalls`, then adds `counts` and optionally `times` as struct sysctl nodes backed directly by the global arrays.

Integration: counter increments happen elsewhere through `sys/syscall_stats.h`; this file owns storage and sysctl publication.

Reliability notes: no runtime logic exists when `SYSCALL_STATS` is disabled. The sysctls expose raw fixed-size kernel arrays; readers must know the syscall table layout for interpretation.
