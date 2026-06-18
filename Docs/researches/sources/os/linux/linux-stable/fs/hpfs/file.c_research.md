# File Research: sources/os/linux/linux-stable/fs/hpfs/file.c

## Purpose

Implements HPFS regular-file operations, page-cache integration, block mapping, truncation, fsync, and fiemap.

## Main Entry Points

- `hpfs_bmap()` and `hpfs_get_block()`
- `hpfs_truncate()`
- `hpfs_read_folio()`, `hpfs_readahead()`, `hpfs_writepages()`
- `hpfs_write_begin()` / `hpfs_write_end()`
- `hpfs_fiemap()`
- `hpfs_file_ops`, `hpfs_file_iops`, `hpfs_aops`

## Control Flow And State

Block mapping first uses a small per-inode allocation cache, then consults the fnode B+ tree. Writes are contiguous-growth oriented: allocation is only allowed when the requested block is exactly at `mmu_private`. New blocks are appended through `hpfs_add_sector_to_btree()`. Write failures beyond EOF truncate page cache and metadata back. Successful writes mark the HPFS inode dirty for later fnode/dirent update.

`fiemap` uses iomap read-only mapping, respecting hotfix boundaries.

## Dependencies

Uses mpage, iomap, buffer-head block mapping, anode allocation-tree helpers, hotfix remapping, and inode writeback helpers.

## Risks

The write path assumes append-style block growth and calls `BUG()` on unexpected sparse-create attempts. Hotfix remapping can split otherwise contiguous extents. `hpfs_truncate()` requires the HPFS lock and directly mutates allocation trees.
