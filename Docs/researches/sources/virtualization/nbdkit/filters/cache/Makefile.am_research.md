# File Research: sources/virtualization/nbdkit/filters/cache/Makefile.am

Purpose: builds the Unix-only cache filter module.

Key details:
- Guarded by `!IS_WINDOWS` because reclaim/hole punching and related filesystem behavior are OS-specific.
- Builds `nbdkit-cache-filter.la` from `blk.c`, `blk.h`, `cache.c`, `cache.h`, `lru.c`, `lru.h`, `reclaim.c`, and `reclaim.h`.
- Includes nbdkit headers, generated headers, `common/bitmap`, `common/include`, and `common/utils`.
- Links bitmap and utility libraries plus Windows import support placeholder.
- Adds linker symbol script when configured.
- Generates `nbdkit-cache-filter.1` from POD when available.

Integration notes:
- This Makefile binds together the cache front-end, block store, LRU heuristic, and reclaim state machine.
