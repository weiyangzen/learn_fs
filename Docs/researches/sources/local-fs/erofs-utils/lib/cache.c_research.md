# File Research: sources/local-fs/erofs-utils/lib/cache.c

## Purpose
Implements the EROFS userspace buffer manager used by mkfs-style writers to allocate, pack, map, flush, drop, and account metadata/data buffer blocks.

## Main Concepts
- `erofs_bufmgr`: owns watermeter buckets, bitmap accelerators, block list, tail block address, metablk count, data-unit alignment, and output vfile.
- `erofs_buffer_block`: block-sized logical allocation unit, initially unmapped or mapped.
- `erofs_buffer_head`: individual allocation inside a buffer block with a flush operation.

## Important Functions
- `erofs_buffer_init()`: initializes watermeters, bucket bitmaps, sentinel block, tail block, and output vfile.
- `__erofs_battach()`: core placement routine for attaching/reserving space in a buffer block with alignment and inline-boundary constraints.
- `erofs_bh_balloon()`: grows the tail buffer head.
- `erofs_bfind_for_attach()`: searches watermeter buckets for a reusable block that best fits a new allocation.
- `erofs_balloc()`: allocates a new buffer head, reusing an existing block when possible.
- `erofs_battach()`: attaches a follow-on buffer head after an existing one.
- `erofs_mapbh()` / `__erofs_mapbh()`: assigns physical block addresses and honors data-stripe alignment.
- `erofs_bflush()`: maps and flushes buffer blocks before a boundary.
- `erofs_bdrop()`: drops/revokes a buffer head and frees the block if empty.
- `erofs_total_metablocks()`: returns metadata block accounting.
- `erofs_buffer_exit()`: abort-flushes remaining buffers and frees manager state.

## Interactions
- Flush callbacks are supplied through `struct erofs_bhops`; built-ins include direct drop and skip-write.
- Used by compression, blob dumping, superblock/config writing, inode writing, and other mkfs paths.

## Notes
Watermeter buckets are indexed by used bytes and mapped/unmapped state to reduce fragmentation and find high-fill placements.
