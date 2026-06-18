# File Research: sources/os/bsd/netbsd-src/sys/sys/resourcevar.h

Read completely: 133 lines.

This kernel/KMEMUSER-only header defines internal process accounting and resource-limit state. `struct uprof` stores profiling buffers and deferred AST accounting, while `struct pstats` stores per-process usage, child usage, interval timers, profiling state, and process start time.

The kernel-only `struct plimit` stores copy-on-write resource limits, core-file naming state, reference count, lock, writeability marker, and saved limit pointer. APIs cover profiling accounting, runtime usage calculation, limit copying/refcounting/private copies, core name updates, resource subsystem init, usage aggregation, pstats copy/free, and `getrusage1`.

Risks: `plimit` is shared after fork and privatized on mutation, so lock/refcount discipline is central. Profiling uses deferred fields updated from AST paths.
