# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vmem_impl.h

## Role

`vmem_impl.h` defines implementation-private structures for the vmem allocator: segments, freelists, hash tables, quantum caches, kstats, and arena metadata.

## Key Structures

`vmem_seg_t` represents an arena segment. Its first four fields intentionally match `vmem_freelist_t`: start, end, next-of-kind, previous-of-kind. It also has arena links, type, imported flag, audit depth, and optional audit metadata such as thread, timestamp, and stack.

`vmem_freelist_t` is the size-class free-list header format.

`struct vmem` contains:
- arena name, lock, and condition variable,
- arena ID and allocation-failure injection field,
- creation flags, quantum sizing, qcache limits, and import minimum,
- source import/free callbacks and parent source arena,
- global vmem list linkage,
- kstat pointer and embedded kstat data,
- segment freelist,
- allocated-segment hash table and initial hash table,
- free-list bitmap,
- sentinel segment and next-fit rotor,
- quantum cache pointers,
- power-of-two freelists.

## Helpers

The file defines hash indexing macros, `VS_SIZE()`, constants for name length, initial hash size, qcache count, freelist count, and audit stack depth.

`vmem_kstat_t` tracks memory in use/import/total, source ID, allocation/free/wait/fail counts, lookup/search counts, population waits/failures, and `vmem_contains()` metrics.

## Research Notes

This header is for allocator internals, not consumers. The freelist/segment layout coupling is explicit and should be preserved. Changes here require matching changes in vmem implementation and observability consumers.
