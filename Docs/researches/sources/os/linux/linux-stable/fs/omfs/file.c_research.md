# File Research: sources/os/linux/linux-stable/fs/omfs/file.c

## Scope

This file implements OMFS regular-file extent mapping, growth, truncate-to-zero cleanup, page-cache address-space operations, file operations, and setattr.

## Main APIs

- `omfs_make_empty_table()` initializes an extent table with a terminator entry.
- `omfs_shrink_inode()` frees all file extents and continuation blocks when file size is zero.
- `omfs_get_block()` maps logical file blocks to disk blocks and optionally extends the file.
- Address-space ops provide buffered read, readahead, writeback, write-begin/end, bmap, invalidation, dirtying, and migration.
- File ops use generic read/write/mmap/splice/llseek plus `simple_fsync`.
- `omfs_setattr()` validates size changes, truncates page cache, invokes OMFS truncation, copies attributes, and marks the inode dirty.

## Control Flow

- Extent tables live in the inode block at `OMFS_EXTENT_START`; continuation tables would start at `OMFS_EXTENT_CONT`.
- `find_block()` walks extent entries, converting OMFS clusters to Linux block numbers and returning how many blocks remain contiguous.
- `omfs_grow_extent()` first tries to extend the last extent by allocating the next exact block. If that fails, it allocates a new range and inserts a new extent before the terminator.
- Continuation-block creation is explicitly TODO; if the initial extent table fills, growth fails with `-EIO`.
- `omfs_shrink_inode()` supports only truncate to zero, clears bitmap ranges for every data extent, resets extent tables, frees continuation blocks, and leaves partial truncation unsupported.

## Risks And Invariants

- Partial truncate is unsupported; nonzero target size returns `-EIO` from shrink and `omfs_setattr()` has already adjusted `i_size` before calling `omfs_truncate()`.
- Hole handling is TODO. Writes extend at the end of available extents rather than representing sparse holes.
- Continuation extent creation is TODO, limiting maximum fragmented file extent count.
- Extent table corruption checks rely on `extent_count <= max_extents` and `omfs_is_bad()` self-pointer validation.
