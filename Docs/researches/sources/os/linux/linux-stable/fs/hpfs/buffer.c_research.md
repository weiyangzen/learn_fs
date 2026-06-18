# File Research: sources/os/linux/linux-stable/fs/hpfs/buffer.c

## Purpose

Provides HPFS sector and four-sector buffer mapping helpers with hotfix remapping and readahead.

## Main Entry Points

- `hpfs_search_hotfix_map()` and `_for_range()`
- `hpfs_prefetch_sectors()`
- `hpfs_map_sector()` / `hpfs_get_sector()`
- `hpfs_map_4sectors()` / `hpfs_get_4sectors()`
- `hpfs_brelse4()` and `hpfs_mark_4buffers_dirty()`

## Control Flow And State

Reads check the hotfix map before buffer access. Four-sector mapping validates alignment and either returns contiguous buffer memory or allocates a temporary 2048-byte concatenation buffer. Dirtying a noncontiguous four-sector buffer copies the temporary data back into the four buffer heads before marking them dirty.

## Dependencies

Uses buffer-head APIs, block readahead, HPFS global lock assertions, and superblock hotfix arrays.

## Risks

Callers must hold the HPFS global lock. Noncontiguous four-sector buffers require explicit `hpfs_mark_4buffers_dirty()` before release or updates are lost. Hotfix ranges suppress merged readahead and merged iomap ranges elsewhere.
