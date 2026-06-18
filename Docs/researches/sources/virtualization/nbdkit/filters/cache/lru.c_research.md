# File Research: sources/virtualization/nbdkit/filters/cache/lru.c

Purpose: approximate LRU tracking for cache reclaim.

Key details:
- Uses two one-bit-per-block bitmaps to track recently accessed blocks.
- `lru_set_size` resizes both bitmaps and sets target window `N` to roughly a quarter of either max cache size or virtual image size, with minimum 100 blocks.
- `lru_set_recently_accessed` sets the block in `bm[0]`; when `c0 >= N/2`, it swaps `bm[0]` and `bm[1]`, clears the new `bm[0]`, and resets counters.
- `lru_has_been_recently_accessed` checks both bitmaps.
- Intended as a low-memory heuristic rather than an exact recency list.

Integration notes:
- Reclaim uses this to prefer punching holes in blocks outside the recent-access window.
