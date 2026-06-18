# File Research: sources/os/bsd/netbsd-src/sys/sys/sched.h

Read completely: 285 lines.

This header defines POSIX scheduling policy constants, CPU set interfaces, Linux-compatible clone flags, CPU accounting states, and kernel scheduler interfaces. Public pieces include `struct sched_param`, `SCHED_*`, cpuset creation/manipulation wrappers, and internal affinity/parameter syscalls.

For kernel/KMEMUSER it defines `struct schedstate_percpu`, including per-CPU scheduler locks, processor-set data, CPU state counters, runqueue state, priority bitmap, and queue pointers. Kernel APIs cover scheduler initialization, CPU attach, periodic accounting, runqueue enqueue/dequeue, rescheduling, fork/exit hooks, wake/sleep hooks, CPU selection, preemption, context switching, idle, suspend, and scheduling parameter syscalls.

Risks: `schedstate_percpu` fields have explicit lock-domain annotations. Misusing fields outside their lock or CPU ownership can corrupt run queues or accounting.
