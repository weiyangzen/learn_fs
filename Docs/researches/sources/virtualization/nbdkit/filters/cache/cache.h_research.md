# File Research: sources/virtualization/nbdkit/filters/cache/cache.h

Purpose: shared configuration/state declarations for cache filter components.

Key details:
- Declares `enum cache_mode` with writeback, writethrough, and unsafe modes.
- Exposes global `blksize`, `min_block_size`, `max_size`, `hi_thresh`, and `lo_thresh`.
- Declares cache-on-read mode enum `COR_OFF`, `COR_ON`, `COR_PATH`, plus `cor_path`.
- Declares `cache_on_read()` for `blk.c`.

Integration notes:
- This header couples `cache.c`, `blk.c`, `lru.c`, and `reclaim.c` around shared runtime policy.
