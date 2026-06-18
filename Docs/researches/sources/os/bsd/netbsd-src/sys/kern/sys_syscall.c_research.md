# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_syscall.c

Implements machine-independent indirect syscall dispatch. The file is parameterized by `SYS_SYSCALL`, so it can be included for native and compat indirect syscall implementations.

Key behavior:
- `SYS_SYSCALL_biglockcheck`: diagnostic-only assertion that a syscall did not leak the kernel big lock.
- `SYS_SYSCALL`: reads the indirect syscall number, masks it by `SYS_NSYSENT - 1`, counts it, rejects indirect-to-indirect syscalls, dispatches through the emulation’s `sysent` table, and integrates tracing.

Trace and compat handling:
- Fast path skips tracing when `p_trace_enabled` is false.
- Trace path calls `trace_enter`, syscall handler, and `trace_exit`.
- Under `NETBSD32_SYSCALL`, syscall args are widened into a local `register_t` array for tracing.

Research notes:
- This file is small but important syscall-table glue. It has no filesystem-specific logic, but all indirect syscall behavior depends on this dispatch path.
