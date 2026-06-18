# File Research: sources/os/linux/linux-stable/fs/gfs2/aops.c

## Purpose
Implements GFS2 address-space operations for reading, readahead, writeback, bmap, folio invalidation/release, and journaled-data writeback.

## Key Interfaces
- `gfs2_jdata_writeback()` writes journaled-data folios while an exclusive glock is held.
- `gfs2_internal_read()` reads internal GFS2 files through the page cache.
- `adjust_fs_space()` updates statfs data after filesystem growth.
- `gfs2_release_folio()` releases journal buffer metadata.
- `gfs2_set_aops()` selects normal or journaled-data address-space operations.

## Control Flow And Behavior
Normal writeback uses iomap writepages and may force AIL flushing if no pages were written. Journaled-data writeback uses a custom write-cache loop that starts transactions before locking folios, marks checked folios, adds data buffers to transactions, and flushes the log during synchronous writeback.

Reads choose between iomap reads, stuffed-file reads from the dinode, and mpage reads for journaled data. Readahead skips stuffed files, uses mpage for journaled data, and iomap for ordinary files. Invalidation/discard paths remove buffers from GFS2 journal/AIL tracking before releasing them.

## Dependencies
Uses GFS2 bmap/iomap operations, glocks, log/transaction APIs, metadata I/O, quota/statfs helpers, buffer heads, folios, mpage, and iomap writeback.

## Risks And Invariants
Journaled-data writeback must start transactions before folio locks. Stuffed file reads must synthesize zero folios for extended but not yet unstuffed cases. Buffer release cannot free buffers still dirty, pinned, referenced, or attached to an active transaction.
