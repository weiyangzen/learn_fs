# File Research: sources/os/bsd/netbsd-src/sys/sys/kthread.h

Kernel-only kernel-thread API. It defines creation flags for idle creation, MPSAFE behavior, interrupt handlers, time-sharing priority, and must-join lifecycle. It declares system initialization, formatted-name creation, exit, join, and FPU enter/exit routines with MD hooks.

The header depends on `sys/proc.h` and is not user-visible. Risks include join obligations for `KTHREAD_MUSTJOIN`, choosing correct locking/kernel-lock behavior, and FPU state handling in kernel threads.
