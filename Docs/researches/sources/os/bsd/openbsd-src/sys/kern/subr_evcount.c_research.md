# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_evcount.c

## Role

Implements kernel event counters, mainly for interrupt/event statistics exposed through sysctl. It supports both simple scalar counters and later conversion to per-CPU counters.

## Key Behavior

- `evcount_attach()` initializes an `evcount`, assigns a monotonically increasing ID, records its name/data pointer, and inserts it into the global list.
- `evcount_percpu()` moves counters to a pending per-CPU initialization list before per-CPU setup is complete, or allocates per-CPU counter storage immediately afterward.
- `evcount_init_percpu()` allocates per-CPU counters for pending entries, migrates existing scalar counts into counter slot zero, and returns them to the main list.
- `evcount_detach()` removes a counter and frees per-CPU storage if present.
- `evcount_inc()` increments either the per-CPU counter or scalar count.
- `evcount_sysctl()` reports interrupt counter count, counter values, names, and optional vector data through `KERN_INTRCNT_*` nodes.

## Interfaces And Dependencies

Uses `TAILQ`, `struct evcount`, sysctl helpers, interrupt priority masking for scalar reads, and `counters_alloc/read/free/inc()` from the per-CPU counter subsystem.

## Notes

The design allows early boot counters to exist before per-CPU memory is available, then converts them without losing accumulated counts.
