# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_busdma_bufalloc.c

## Purpose
Provides UMA-backed buffer allocation pools for busdma memory allocation paths, plus optional uncacheable allocation hooks.

## Main Elements
- `struct busdma_bufalloc`: stores minimum allocation size and a fixed array of size-class zones.
- `busdma_bufalloc_create()`: creates power-of-two UMA zones from at least 32 bytes up to `PAGE_SIZE`, with each zone aligned to its size and optional custom slab alloc/free functions.
- `busdma_bufalloc_destroy()`: destroys all created UMA zones and frees the allocator.
- `busdma_bufalloc_findzone()`: finds the smallest zone able to satisfy a requested size, or returns NULL for larger-than-page allocations.
- `busdma_bufalloc_alloc_uncacheable()` / `busdma_bufalloc_free_uncacheable()`: allocate/free uncacheable memory with `kmem_alloc_attr_domainset()` when `VM_MEMATTR_UNCACHEABLE` is available.

## Dependencies And Integration
Used by busdma backends implementing `bus_dmamem_alloc()`. Depends on UMA, VM kernel allocation, domainsets, busdma buffer-zone definitions, and `M_DEVBUF`.

## Risk Notes
The fixed 12-zone array assumes `PAGE_SIZE <= 65536`; larger pages intentionally fail compilation. UMA contiguity is only guaranteed up to a page, so larger allocations must use page-oriented allocators. Uncacheable allocation panics if the platform lacks `VM_MEMATTR_UNCACHEABLE`.
