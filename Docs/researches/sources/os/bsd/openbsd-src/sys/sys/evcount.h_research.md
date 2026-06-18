# File Research: sources/os/bsd/openbsd-src/sys/sys/evcount.h

This kernel-only header defines lightweight event counters.

Key definitions:
- `struct evcount` with main counter, id, name, user data, optional per-CPU counter storage, and global queue linkage.

Kernel APIs:
- `evcount_attach`
- `evcount_detach`
- `evcount_inc`
- `evcount_init_percpu`
- `evcount_percpu`
- `evcount_sysctl`

Behavior and integration:
- Only active under `_KERNEL`.
- Uses `<sys/queue.h>` and forward-declares `struct cpumem`.

Risk notes:
- Counters can be per-CPU or global; sysctl aggregation must understand `ec_percpu`.
