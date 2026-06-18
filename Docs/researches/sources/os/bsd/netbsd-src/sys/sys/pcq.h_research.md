# File Research: sources/os/bsd/netbsd-src/sys/sys/pcq.h

## Purpose
Declares an opaque producer/consumer queue API for kernel use.

## Main API
- Opaque type: `pcq_t`.
- Maximum length: `PCQ_MAXLEN`.
- Functions: `pcq_put`, `pcq_peek`, `pcq_get`, `pcq_maxitems`, `pcq_create`, `pcq_destroy`.

## Dependencies
Includes `sys/kmem.h`; APIs are kernel-only.

## Risks and Notes
The queue object is opaque, so users rely on the implementation for synchronization and memory ordering. `pcq_put` returns boolean success/failure, likely for full-queue handling.
