# File Research: sources/os/bsd/dragonflybsd/sys/sys/sched.h

This header defines the POSIX scheduling policy ABI and userland scheduling function declarations.

Key responsibilities:
- Defines scheduling policies:
  - `SCHED_FIFO`
  - `SCHED_OTHER`
  - `SCHED_RR`
- Defines `struct sched_param` with `sched_priority`.
- Declares POSIX scheduler APIs:
  - `sched_setparam()`
  - `sched_getparam()`
  - `sched_setscheduler()`
  - `sched_getscheduler()`
  - `sched_yield()`
  - `sched_get_priority_max()`
  - `sched_get_priority_min()`
  - `sched_rr_get_interval()`
- Under BSD visibility, includes CPU mask support and declares affinity APIs:
  - `sched_setaffinity()`
  - `sched_getaffinity()`
  - `sched_getcpu()`
- Defines `cpu_set_t` and FreeBSD-compatible `cpuset_t` as `cpumask_t`.

Important invariants:
- The userland declarations are excluded under `_KERNEL`.
- BSD affinity support depends on `<sys/cpumask.h>` and visibility gates.

Research notes:
- This is a POSIX/BSD user ABI header for scheduler control, not DragonFly's internal scheduler data structure header.
