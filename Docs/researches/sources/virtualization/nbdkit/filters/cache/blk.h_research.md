# File Research: sources/virtualization/nbdkit/filters/cache/blk.h

Purpose: declares the cache filter’s block-store API.

Key details:
- Exposes lifecycle: `blk_init`, `blk_free`, and `blk_set_size`.
- Declares block read/cache/write paths: `blk_read`, `blk_read_multiple`, `blk_cache`, `blk_writethrough`, and `blk_write`.
- Defines `block_callback` and `for_each_dirty_block` for flush scanning.
- Documents that callers must hold an exclusive lock for all operations after initialization/free.

Integration notes:
- This header is the contract between `cache.c` and the temp-file/bitmap implementation in `blk.c`.
