# File Research: sources/virtualization/nbdkit/filters/cache/reclaim.c

Purpose: cache space reclaim mechanism using hole punching.

Key details:
- If `HAVE_CACHE_RECLAIM` is unavailable, `reclaim` is a no-op.
- When enabled, state machine transitions from not reclaiming to LRU reclaim once allocated cache space crosses the high threshold.
- Continues reclaiming until allocation drops below the low threshold.
- Reclaims up to two blocks per `reclaim` call.
- Starts with blocks not recently accessed according to `lru_has_been_recently_accessed`; if exhausted, switches to reclaiming any cached block.
- `reclaim_block` punches a hole with `fallocate(FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)` and clears the cache bitmap entry.

Risk notes:
- Reclaim assumes dirty data has already been handled or that clearing the bitmap is correct for the current cache mode; call ordering and state meaning in `blk.c` are important.
- Lack of hole-punch support disables reclaim at compile time.
