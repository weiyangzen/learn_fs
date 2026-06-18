# File Research: sources/os/bsd/netbsd-src/sys/sys/userret.h

Read completely: 68 lines.

Defines machine-independent work before returning to user mode.

Key elements:
- Inline `mi_userret(struct lwp *)` disables preemption, asserts no leaked kernel lock or block count, checks reschedule/user-return exception flags, reenables preemption, and calls `lwp_userret()` for exceptional work.
- Adds lockdebug and psref barriers after user-return handling.
- Asserts no preemption disable count and no outstanding psrefs remain.

Risks and notes:
- This is a hot syscall/trap return path.
- Assertions enforce critical invariants: no biglock leak, no blocked count leak, no psref leak.
