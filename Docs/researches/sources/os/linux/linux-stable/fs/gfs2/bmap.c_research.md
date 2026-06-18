# File Research: sources/os/linux/linux-stable/fs/gfs2/bmap.c

## Purpose
Implements GFS2 block mapping, iomap integration, stuffed-file unstuffing, extent allocation, truncate/grow/shrink, hole punching, metadata-tree deallocation, journal extent caching, and writeback iomap callbacks.

## Key Interfaces
- Mapping/allocation: `gfs2_block_map()`, `gfs2_iomap_get()`, `gfs2_iomap_alloc()`, `gfs2_get_extent()`, `gfs2_alloc_extent()`.
- Size/deallocation: `gfs2_setattr_size()`, `gfs2_truncatei_resume()`, `gfs2_file_dealloc()`, `__gfs2_punch_hole()`.
- Stuffed data: `gfs2_unstuff_dinode()`.
- Journal mapping: `gfs2_map_journal_extents()` and `gfs2_free_journal_extents()`.
- Iomap tables: `gfs2_iomap_ops`, `gfs2_iomap_write_ops`, and `gfs2_writeback_ops`.

## Control Flow And Behavior
A compact `metapath` represents the path through dinode and indirect blocks. Lookup builds or walks metadata paths, computes holes and extents, and returns inline, mapped, or hole iomaps. Write begin allocates quota/reservation, starts transactions, unstuffs if needed, grows metadata height/depth, allocates indirect/data blocks, and marks new iomaps. Iomap end releases reservations/quotas and punches back newly allocated unwritten tail blocks after short writes.

Truncation first updates size and marks `GFS2_DIF_TRUNC_IN_PROG`, truncates page cache with special revoke handling for jdata files, walks metadata bottom-up/right-to-left to free data and indirect blocks per resource group, then clears truncate-in-progress. Hole punching zeros partial blocks, flushes page cache range, journals/truncates cached data, and frees whole-block ranges.

## Dependencies
Uses GFS2 glocks, metadata I/O, rgrp allocation/freeing, quota, statfs, transactions, ordered write tracking, log thresholds, iomap, buffer heads, and tracepoints.

## Risks And Invariants
Metadata deallocation is transaction-boundary sensitive: dinode block counts are rewritten at boundaries for crash recovery. Direct writes to holes/stuffed files return `-ENOTBLK` to fall back to buffered I/O. No open transaction may surround `gfs2_block_zero_range()` because iomap write starts its own transactions. `GFS2_DIF_TRUNC_IN_PROG` enables truncate resume after interruption.
