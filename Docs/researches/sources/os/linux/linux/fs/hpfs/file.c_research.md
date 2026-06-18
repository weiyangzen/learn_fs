# File Research: sources/os/linux/linux/fs/hpfs/file.c

Purpose: Implements HPFS regular-file VFS and address-space operations, including block mapping, page-cache I/O, writeback, truncate, fiemap, and fsync.

Key functions:
- `hpfs_file_release()` writes dirty inode metadata on close.
- `hpfs_file_fsync()` writes file ranges and syncs the block device.
- `hpfs_bmap()` maps file-sector numbers through the fnode/anode B+ tree and inode extent cache.
- `hpfs_truncate()` truncates the allocation tree and writes inode metadata.
- `hpfs_get_block()` maps or allocates blocks for buffer-head based I/O.
- `hpfs_iomap_begin()` provides read-only iomap mapping for fiemap.
- `hpfs_read_folio()`, `hpfs_readahead()`, and `hpfs_writepages()` delegate to mpage helpers.
- `hpfs_write_begin()` and `hpfs_write_end()` handle contiguous writes and mark inode metadata dirty.
- `hpfs_fiemap()` exposes extents through iomap.
- `hpfs_aops`, `hpfs_file_ops`, and `hpfs_file_iops` wire VFS integration.

Dependencies and integration:
- Uses `anode.c` B+ tree helpers, hotfix range handling, HPFS global lock, and Linux mpage/iomap helpers.

Risk notes:
- Block allocation only permits append at `mmu_private`; unexpected non-append create mappings trigger `BUG()`.
- HPFS setattr rejects file extension through truncate; growth occurs through writes.
