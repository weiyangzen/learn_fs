# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_datablock.c

## Purpose
Implements V7FS data block allocation, deallocation, file block tree growth/shrink, logical-to-physical block lookup, and iteration over file payload blocks.

## Main Interfaces
- `datablock_number_sanity()` validates data-sector numbers against the mounted superblock.
- `v7fs_datablock_allocate()` pops from the superblock free-block cache, refreshes chained free-block lists with `v7fs_freeblock_update()`, zeroes the selected block, and returns `ENOSPC`/`EIO` on failure.
- `v7fs_datablock_foreach()` walks direct, single, double, and triple indirect block references and calls a callback with each block and payload size.
- `v7fs_datablock_last()` maps a file offset to the backing block using `v7fs_datablock_addr()` and indirect-link readers.
- `v7fs_datablock_expand()`, `v7fs_datablock_contract()`, and `v7fs_datablock_size_change()` maintain inode size and block/index allocation.

## Implementation Notes
The file models classic V7 addressing: direct entries plus single/double/triple indirect blocks. Indirect block contents are sector addresses converted with `V7FS_VAL32()`. Freeing an indirect level unlinks child entries before returning data/index blocks to the free list. Metadata changes are written immediately through `v7fs_inode_writeback()` and `fs->io.write()`.

## Dependencies
Uses `v7fs_superblock` free-block state, scratch buffers from `v7fs_io.c`, endian helpers, inode writeback, and the block I/O callback table in `struct v7fs_self`.
