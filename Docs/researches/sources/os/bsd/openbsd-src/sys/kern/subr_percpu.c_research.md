# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_percpu.c

## Role

Implements per-CPU memory allocation wrappers and per-CPU counters, with separate multiprocessor and uniprocessor implementations.

## Key Behavior

- In multiprocessor builds, `percpu_init()` initializes a pool of `struct cpumem` arrays sized for `ncpusfound`.
- `cpumem_get()`/`cpumem_put()` allocate and free one object per CPU from a supplied pool.
- `cpumem_malloc()`/`cpumem_free()` allocate and free cacheline-rounded per-CPU malloc storage.
- `cpumem_malloc_ncpus()` reuses CPU 0 boot memory and allocates the remaining CPU slots.
- `cpumem_first()` and `cpumem_next()` provide iteration over per-CPU slots.
- `counters_alloc()` reserves an extra generation word plus counter slots per CPU; `counters_free()` releases them.
- `counters_read()` uses a generation counter protocol with memory barriers to read stable per-CPU counter snapshots and sum them.
- `counters_zero()` clears counters and generation words across CPUs.
- In uniprocessor builds, all APIs collapse to a single allocation and `counters_read()`/`counters_zero()` protect access with `splhigh()`.

## Interfaces And Dependencies

Uses pools, malloc types, cacheline sizing, memory barriers, `yield()`, interrupt priority masking, and counter macros/functions declared in `sys/percpu.h`.

## Notes

The MP counter layout reserves a generation word before the counters so writers can make readers retry when observing an update in progress. The UP implementation preserves API shape without cacheline or multi-slot overhead.
