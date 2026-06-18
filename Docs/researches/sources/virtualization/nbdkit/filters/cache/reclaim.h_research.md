# File Research: sources/virtualization/nbdkit/filters/cache/reclaim.h

Purpose: declares cache reclaim availability and entry point.

Key details:
- Defines `HAVE_CACHE_RECLAIM` when `FALLOC_FL_PUNCH_HOLE` is available.
- Declares `reclaim(int fd, struct bitmap *bm)`.
- Documents that reclaim must be called with the block/cache lock held.

Integration notes:
- Used by `cache.c`/`blk.c` to keep temp cache allocation below configured limits.
