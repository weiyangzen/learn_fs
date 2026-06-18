# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_syscall.c

Read completely: 310 lines.

Implements dynamic syscall module plumbing and syscall tracing hooks for NetBSD emulations.

Module-backed syscalls:
- `sys_nomodule()` is the placeholder for autoloadable syscall entries. With `MODULAR`, it takes `kernconfig_lock()`, checks whether the syscall entry was filled while waiting, looks up the emulation's autoload table, attempts `module_autoload()`, and returns `ERESTART` if the syscall should be retried. Without success, it falls through to `sys_nosys()`.
- `syscall_establish()` installs a package of syscall entry points after validating all requested slots are currently `sys_nomodule` or `sys_nosys`.
- `syscall_disestablish()` first gates removed entries back to `sys_nomodule` or `sys_nosys`, runs `xc_barrier()` for visibility across CPUs, scans all LWPs for active `l_sysent` references, and rolls back with `EBUSY` if any syscall is still in use.

Tracing:
- `trace_is_enabled()` reports whether syscall tracing is active through `SYSCALL_DEBUG`, ktrace syscall/sysret flags, or ptrace syscall tracing.
- `trace_enter()` emits DTrace syscall-entry hooks, optional syscall-debug output, ktrace syscall records, and ptrace syscall-entry stops through `proc_stoptrace(TRAP_SCE)`. It returns `EJUSTRETURN` when the tracer will emulate the syscall.
- `trace_exit()` emits DTrace syscall-return hooks, optional debug return output, ktrace sysret records, ptrace syscall-exit stops through `proc_stoptrace(TRAP_SCX)`, and clears `PSL_SYSCALLEMU`.

Concurrency and notes:
- Establish/disestablish require `kernconfig_lock()` to be held.
- Disestablish uses both a cross-call barrier and `alllwp` scan because a CPU may already have posted a `struct sysent *` in an LWP.
- This file ties directly into `kern_sig.c` through ptrace syscall-stop handling.
