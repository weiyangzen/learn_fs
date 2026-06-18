# File Research: sources/os/bsd/dragonflybsd/sys/sys/resource.h

This header defines DragonFly BSD user/kernel resource accounting ABI: priorities, resource usage records, resource limits, load averages, CPU state indexes, and public resource syscalls.

Key responsibilities:
- Defines `id_t` and `rlim_t` where not already declared.
- Defines process priority targets and ranges:
  - `PRIO_PROCESS`, `PRIO_PGRP`, `PRIO_USER`
  - BSD-visible `PRIO_MIN`, `PRIO_MAX`, `IOPRIO_MIN`, `IOPRIO_MAX`
- Defines `struct rusage` for user/system time, RSS, page faults, block I/O, messages, signals, and context switches.
- Defines `struct __wrusage` as paired self/children usage under BSD visibility.
- Defines resource limit IDs:
  - POSIX/common: `RLIMIT_CPU`, `RLIMIT_FSIZE`, `RLIMIT_DATA`, `RLIMIT_STACK`, `RLIMIT_CORE`, `RLIMIT_NOFILE`, `RLIMIT_AS`
  - BSD-visible: `RLIMIT_RSS`, `RLIMIT_MEMLOCK`, `RLIMIT_NPROC`, `RLIMIT_SBSIZE`, `RLIMIT_POSIXLOCKS`
- Defines `struct rlimit`, `RLIM_INFINITY`, saved-limit aliases, and optional `_RLIMIT_IDENT` string table.
- Defines BSD-visible `struct loadavg` and `CP_*` CPU state indexes.
- Exposes userland declarations for `getpriority`, `setpriority`, `getrlimit`, `setrlimit`, `getrusage`, and BSD `ioprio_get`/`ioprio_set`.
- Exposes kernel `averunnable` and `dosetrlimit()`.

Important invariants:
- `RLIMIT_CPU` is documented as milliseconds in this ABI.
- `RLIM_INFINITY` is the maximum signed 63-bit `rlim_t` value.
- `RLIM_NLIMITS` is BSD-visible and currently 12.
- `ru_first`/`ru_last` mark the aggregatable counter range inside `struct rusage`.

Research notes:
- This is a stable syscall/user ABI header with visibility-gated BSD additions.
- The `getpriority`/`setpriority` prototypes still take `int` for the id argument, with comments noting XSI would prefer `id_t`.
