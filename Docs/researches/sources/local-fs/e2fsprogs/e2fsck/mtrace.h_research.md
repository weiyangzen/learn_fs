# File Research: sources/local-fs/e2fsprogs/e2fsck/mtrace.h

## Purpose

`mtrace.h` is a legacy GNU malloc/debugging declaration header. In this tree it supports optional `MTRACE` instrumentation used by e2fsck passes, for example pass headers guarded by `#ifdef MTRACE`. It declares public allocation functions, internal allocator structures when `_MALLOC_INTERNAL` is defined, allocator hooks, tracing/checking entry points, and memory statistics APIs.

## Main API Surface

Public allocator declarations:

- `malloc(size_t)`
- `realloc(void *, size_t)`
- `calloc(size_t, size_t)`
- `free(void *)`
- `memalign(size_t alignment, size_t size)`
- `valloc(size_t)`

Allocator extension/debug declarations:

- `__morecore` function pointer and `__default_morecore`
- `__malloc_initialized`
- `__free_hook`
- `__malloc_hook`
- `__realloc_hook`
- `mcheck(void (*func)(void))`
- `mtrace(void)`
- `mstats(void)`

The `struct mstats` result exposes total heap bytes, used/free chunk counts, and used/free byte totals.

## Internal Allocator Model

Under `_MALLOC_INTERNAL`, the header exposes the heap layout expected by the allocator implementation:

- Fixed-size heap blocks controlled by `BLOCKLOG`, `BLOCKSIZE`, and `BLOCKIFY`.
- `HEAP` initial heap-table sizing.
- `FINAL_FREE_BLOCKS`, the threshold of trailing free blocks that may be returned to the system.
- `malloc_info`, a union storing either busy-block information or free-cluster linkage.
- `_heapbase`, `_heapinfo`, `_heapindex`, and `_heaplimit` for heap addressing and heap-table scanning.
- `_fraghead[]`, a set of fragment free-list heads.
- `_aligned_blocks`, tracking exact allocations behind aligned returned addresses.
- `_chunks_used`, `_bytes_used`, `_chunks_free`, `_bytes_free` counters.
- `_free_internal()` for allocator-internal freeing.

## Portability Behavior

The header supports pre-ANSI C and C++ consumers:

- `__P(args)` expands to prototypes for C++/ANSI C and empty argument lists otherwise.
- `__ptr_t` is `void *` for ANSI/C++ and `char *` otherwise.
- It defines `NULL`, `size_t`, and `ptrdiff_t` fallbacks for older C environments.
- It conditionally includes `<stddef.h>`, `<stdio.h>`, `<string.h>`, and `<limits.h>`, with `memset`/`memcpy` fallbacks to `bzero`/`bcopy`.

## Integration Notes

This file does not implement allocation or tracing; it only declares interfaces and structures. The e2fsck source uses `MTRACE` guards elsewhere, but this header itself is standalone and has no dependency on e2fsck-specific state.

## Risk Notes

The interfaces are intentionally old and global-hook based. If enabled in modern builds, the most sensitive areas are ABI assumptions around allocator hooks and old C compatibility macros. There is no direct filesystem repair logic here.
