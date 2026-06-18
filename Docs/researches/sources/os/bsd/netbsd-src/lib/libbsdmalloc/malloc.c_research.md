# File Research: sources/os/bsd/netbsd-src/lib/libbsdmalloc/malloc.c

Implements the historical BSD/Caltech bucket allocator plus modern allocation front ends.

Key behavior:
- Uses `sbrk` and fixed power-of-two buckets tracked by `nextf[NBUCKETS]`.
- `malloc` initializes page size, aligns the break, computes the smallest bucket that fits requested size plus overhead, calls `morecore` when needed, marks allocated blocks with `MAGIC`, and returns memory after the overhead header.
- `morecore` obtains at least a page or one large block from `sbrk` and links new blocks into the requested bucket free list.
- `free` validates the magic byte in debug/range-check builds and pushes the block back onto the corresponding free list.
- `realloc` supports the historical “storage compaction” behavior by searching free lists for already-freed blocks via `findbucket`; otherwise it allocates/copies/frees.
- Optional `RCHECK` adds range magic checks; optional `MSTATS` provides `mstats`.
- Adds C11/POSIX front ends: `aligned_alloc`, `calloc`, and `posix_memalign`.
- Provides libc fork hooks `_malloc_prefork`, `_malloc_postfork`, and `_malloc_postfork_child`.

Dependencies:
- `sbrk`, `getpagesize`, libc private `reentrant.h`, and optional debug/range/stat facilities.

Notes and risks:
- This allocator never returns memory to the OS.
- `aligned_alloc` and `posix_memalign` only support alignments up to page size.
- Non-debug invalid frees silently return when the magic byte is wrong.
