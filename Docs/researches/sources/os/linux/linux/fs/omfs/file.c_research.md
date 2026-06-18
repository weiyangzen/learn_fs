# File Research: sources/os/linux/linux/fs/omfs/file.c

OMFS regular file and address-space operations. This file maps logical file blocks to OMFS extents, grows extent tables during writes, truncates files to zero, and wires the driver into generic buffered I/O helpers.

Main responsibilities:
- Initialize empty OMFS extent tables with a sentinel terminator.
- Shrink regular files by freeing all extents when file size becomes zero.
- Grow the current extent or add a new extent when writeback maps an unmapped block.
- Map logical file blocks to physical disk blocks for read, write, readahead, writeback, and bmap.
- Implement setattr-driven size changes.

Extent behavior:
- `omfs_extent` tables contain normal entries followed by a terminator entry.
- `omfs_max_extents()` calculates how many extent entries fit after the table offset.
- `find_block()` scans extent entries and maps a logical block into a physical block plus contiguous remainder.
- `omfs_grow_extent()` first tries to extend the last extent by allocating the immediately following block; otherwise it allocates a new cluster-sized range and inserts a new extent entry.
- Continuation extent blocks are recognized by the on-disk format, but new continuation allocation is still marked TODO; if the first table fills, growth returns `-EIO`.

Truncate behavior:
- `omfs_shrink_inode()` only supports truncate-to-zero.
- It walks the first extent table and any continuation tables, frees all non-terminator extent ranges, resets each table to empty, and frees continuation inode blocks.
- `omfs_truncate()` calls shrink and marks the inode dirty.
- `omfs_write_failed()` rolls back page cache and truncates if block allocation fails beyond current file size.

VFS integration:
- `omfs_get_block()` is the central block mapper used by buffered read/write, mpage readahead/writepages, and bmap.
- `omfs_read_folio()`, `omfs_readahead()`, `omfs_writepages()`, `omfs_write_begin()`, and `omfs_bmap()` are thin wrappers around generic block helpers.
- `omfs_file_operations` uses generic llseek/read/write, mmap preparation, simple fsync, and splice read.
- `omfs_file_inops` provides `setattr`.
- `omfs_aops` installs buffer-head based dirty, invalidate, read, readahead, writepages, write_begin/end, bmap, and migrate hooks.

Important limits:
- Holes are not implemented.
- Nonzero truncation is not supported by `omfs_shrink_inode()`.
- Extent continuation allocation for growth is not implemented.
