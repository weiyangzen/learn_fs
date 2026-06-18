# File Research: sources/os/bsd/openbsd-src/sys/sys/resource.h

Defines process priority, resource usage, resource limit, and load-average public ABI.

Key contents:
- Priority range and `PRIO_PROCESS`/`PRIO_PGRP`/`PRIO_USER`.
- `RUSAGE_SELF`, `RUSAGE_CHILDREN`, `RUSAGE_THREAD`.
- `struct rusage` with time, RSS, paging, block I/O, IPC, signals, and context-switch counters.
- Resource limits: CPU, file size, data, stack, core, RSS, memlock, process count, open files.
- `RLIM_INFINITY`, saved limit aliases, and `struct rlimit`.
- BSD-visible `struct loadavg`.

Key APIs:
- Kernel: `dosetrlimit`, `donice`, `dogetrusage`.
- Userland: `getpriority`, `getrlimit`, `getrusage`, `setpriority`, `setrlimit`.

Risk notes:
- `RLIMIT_CPU` is documented as milliseconds here, which matters for enforcement and user expectations.
