# File Research: sources/os/bsd/netbsd-src/sys/sys/extent.h

Read completely: 121 lines.

## Purpose
Declares the extent allocator: a kernel resource-range allocator for address, bus, I/O, or similar numeric regions.

## Main Interfaces
- `struct extent_region`: allocated range and flags.
- `struct extent`: named range space, lock/cv, allocated-region list, start/end, behavior flags.
- `struct extent_fixed`: extent with fixed descriptor storage.
- Internal flags: `EXF_FIXED`, `EXF_NOCOALESCE`, `EXF_EARLY`.
- Allocation flags: `EX_WAITOK`, `EX_FAST`, `EX_CATCH`, `EX_NOCOALESCE`, `EX_MALLOCOK`, `EX_WAITSPACE`, `EX_BOUNDZERO`, `EX_EARLY`.
- Alignment/boundary sentinels: `EX_NOALIGN`, `EX_NOBOUNDARY`.
- APIs: `extent_create`, `extent_destroy`, `extent_alloc*`, `extent_alloc_region`, `extent_free`, `extent_print`, `extent_init`.

## Dependencies And Integration
Uses queues, mutexes, and condition variables. Consumers include kernel resource managers and potentially storage/device drivers.

## Risks And Edge Cases
- Early-boot extents skip normal locking.
- Fixed storage can run out unless callers allow allocation or waiting.
- Boundary/alignment arguments alter allocation search behavior.

## Filesystem Relevance
Indirect. Useful for block/device resource allocation underneath filesystems.
