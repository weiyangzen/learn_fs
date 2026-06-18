# File Research: sources/os/linux/linux/fs/jfs/inode.c

## Purpose
Implements JFS inode instantiation, writeback/commit, eviction, dirty marking, block mapping, address-space operations, direct I/O cleanup, and truncation.

## Key Functions
- `jfs_iget()` obtains or reads an inode, calls `diRead()`, then installs inode/file/address-space operations based on file type. It handles regular files, directories, long and fast symlinks, special files, and invalid modes.
- `jfs_commit_inode()` is the fsync/writeback workhorse. It skips deleted or non-JFS-dirty inodes, avoids committing read-only non-special files, starts a transaction, locks `commit_mutex`, retests dirty state, and calls `txCommit()`.
- `jfs_write_inode()` flushes the journal when the inode is VFS-dirty but not JFS `COMMIT_Dirty`, otherwise commits the inode.
- `jfs_evict_inode()` handles zero-link file cleanup, page truncation, possible zero-link extent freeing, dinode freeing, quota release, inode clearing, and active-AG counter cleanup.
- `jfs_dirty_inode()` sets `COMMIT_Dirty` unless the volume is read-only.
- `jfs_get_block()` maps logical blocks through `xtLookup()`, records unrecorded allocated extents on write, or allocates new extents via `extHint()` and `extAlloc()`.
- `jfs_writepages()`, `jfs_read_folio()`, `jfs_readahead()`, `jfs_write_begin()`, `jfs_write_end()`, `jfs_bmap()`, and `jfs_direct_IO()` bridge generic block/page-cache helpers to `jfs_get_block()`.
- `jfs_write_failed()` truncates page cache and JFS extents after failed extending writes.
- `jfs_truncate_nolock()` repeatedly calls `xtTruncate()` inside transactions because JFS truncation may not complete atomically.
- `jfs_truncate()` truncates the partial page, takes the inode write lock, and delegates to `jfs_truncate_nolock()`.

## Address-Space Operations
- `jfs_aops` wires dirty/invalidate folio, read/readahead, writepages, write_begin/end, bmap, direct_IO, and buffer folio migration.

## Dependencies
- Uses dinode read/write paths, extent/xtree allocation, transaction manager, quota infrastructure, page-cache helpers, and JFS locks/macros from `jfs_incore.h`.
- Calls into the allocator through extent code rather than directly invoking `jfs_dmap.c`.

## Notable Behavior
- Fast symlinks are null-terminated defensively to avoid kernel crashes from corrupted on-disk data.
- `jfs_get_block()` treats unrecorded extents as holes for reads and records them for writes.
- Failed direct I/O extending writes trim instantiated blocks beyond `i_size`.
