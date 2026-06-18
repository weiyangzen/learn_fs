# File Research: sources/os/bsd/freebsd-src/sys/sys/busdma_bufalloc.h

## Purpose
`busdma_bufalloc.h` declares a UMA-backed DMA buffer pool manager for platform busdma implementations.

## Main Interfaces
- `struct busdma_bufzone` describes a zone size, UMA zone handle, and name.
- `busdma_bufalloc_t` is an opaque allocator handle.
- `busdma_bufalloc_create()` builds power-of-two buffer zones from a minimum alignment up to page size.
- `busdma_bufalloc_destroy()` tears down an allocator.
- `busdma_bufalloc_findzone()` selects a zone for a requested size.
- Built-in uncacheable alloc/free functions support platforms with `VM_MEMATTR_UNCACHEABLE`.

## Implementation Notes
Buffers in each zone are aligned to their size, making them page-contained and boundary-friendly. The design helps busdma quickly decide whether tag constraints permit using a pooled buffer without bouncing.

## Dependencies and Constraints
Includes `machine/bus.h` and `vm/uma.h`. Minimum alignment is also minimum allocation size and must not be below cache-line size on software-coherent platforms.
