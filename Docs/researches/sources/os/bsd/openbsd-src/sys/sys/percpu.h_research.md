# File Research: sources/os/bsd/openbsd-src/sys/sys/percpu.h

Defines per-CPU memory and per-CPU counter abstractions.

Key contents:
- `CACHELINESIZE` default and `__upunused` helper.
- `struct cpumem`, `struct cpumem_iter`, and `struct counters_ref`.
- Boot-memory macros for multiprocessor and uniprocessor builds.
- Counter boot-memory macros.

Key APIs:
- `cpumem_get`, `cpumem_put`, `cpumem_malloc`, `cpumem_malloc_ncpus`, `cpumem_free`.
- `cpumem_first`, `cpumem_next`, `cpumem_enter`, `cpumem_leave`.
- Counter allocation/read/zero/free functions.
- Inline counter update helpers: `counters_enter`, `counters_leave`, `counters_inc`, `counters_dec`, `counters_add`, `counters_pkt`.

Risk notes:
- Multiprocessor counters use generation values and memory barriers; readers depend on even/odd generation consistency.
