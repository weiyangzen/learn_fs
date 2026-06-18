# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbcache.c

Implements the generic bitmap-cache block allocator used by higher-level bitmap caches.

Key behavior:
- `gx_bits_cache_init` initializes an entire cache with a caller-provided first chunk and resets cache counters/rover.
- `gx_bits_cache_chunk_init` initializes a chunk and, when data is present, marks the full data range as one free block.
- `gx_bits_cache_alloc` tries to allocate a block from the current chunk, merging adjacent free blocks as it scans; when a live entry blocks allocation, it returns that entry for caller eviction.
- Splits oversize free space into an allocated block and a following free block.
- Tracks total allocated bytes, entry count, current allocation rover, and per-chunk allocated bytes.
- `gx_bits_cache_shorten` shrinks an allocated block and creates a following free block.
- `gx_bits_cache_free` marks a block free and updates counters; callers must remove any external references first.

Dependencies:
- Uses bitmap cache structures from `gxbcache.h` and Ghostscript debug/fill helpers.

Research notes:
- The allocator does not own chunk memory; callers allocate chunks and their backing data.
- Allocation failure is cooperative: the caller is expected to evict the returned live entry and retry.
