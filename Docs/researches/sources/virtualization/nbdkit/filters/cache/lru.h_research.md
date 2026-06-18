# File Research: sources/virtualization/nbdkit/filters/cache/lru.h

Purpose: declares the cache filter’s approximate LRU API.

Key details:
- Exposes `lru_init`, `lru_free`, and `lru_set_size`.
- Exposes `lru_set_recently_accessed` for read/write/cache paths.
- Exposes `lru_has_been_recently_accessed` for reclaim selection.

Integration notes:
- This is a small internal interface consumed by `blk.c` and `reclaim.c`.
