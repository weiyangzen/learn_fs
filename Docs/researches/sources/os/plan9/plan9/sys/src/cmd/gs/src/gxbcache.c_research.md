# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbcache.c

Purpose: Implements generic bitmap cache chunk and entry allocation for Ghostscript cached bitmap data.

Key functions:
- `gx_bits_cache_init()` initializes a cache with a caller-provided first chunk.
- `gx_bits_cache_chunk_init()` initializes a chunk and marks its data as one free block.
- `gx_bits_cache_alloc()` attempts to allocate an entry, merging adjacent free blocks and asking the caller to evict occupied entries when needed.
- `gx_bits_cache_shorten()` shrinks an allocated entry and creates a free block from the tail.
- `gx_bits_cache_free()` marks an entry free and updates accounting.

Behavior:
- Cache chunks contain variable-sized blocks headed by `gx_cached_bits_head`.
- Allocation uses `bc->cnext` as a rover in the current chunk.
- If insufficient contiguous free space is found because a live entry is encountered, the function returns `-1` and points `*pcbh` at an entry the caller should free.
- Uses debug fill patterns for allocated/deleted blocks.

Dependencies:
- Depends on `gxbcache.h`, Ghostscript memory debug fill API, and debug logging.

Notable risks:
- `lsize` is cast down to `uint` through macros; callers must keep sizes representable.
- Free-block coalescing happens opportunistically during allocation, not globally.
