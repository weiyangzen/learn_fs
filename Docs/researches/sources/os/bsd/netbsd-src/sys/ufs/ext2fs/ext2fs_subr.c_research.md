# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_subr.c

This small support file provides a directory/block-offset buffer helper and ext2fs inode timestamp update logic.

Key responsibilities:
- Read the filesystem block containing a directory/file offset and return a pointer into it.
- Apply deferred inode timestamp flags to on-disk ext2 dinode fields.

Important functions:
- `ext2fs_blkatoff`: Computes logical block number with `ext2_lblkno`, reads the block using `bread`, optionally returns a pointer adjusted by `ext2_blkoff`, and returns the buffer to the caller.
- `ext2fs_itimes`: If any of `IN_ACCESS`, `IN_CHANGE`, `IN_UPDATE`, or `IN_MODIFY` are set, chooses supplied timestamps or current time, writes atime/mtime/ctime through `EXT2_DINODE_TIME_SET`, increments `i_modrev` on mtime updates, sets `IN_ACCESSED`/`IN_MODIFIED`, and clears the pending timestamp flags.

Important interactions:
- `ext2fs_blkatoff` is used by lookup, directory entry mutation, and rename recomputation code.
- `ext2fs_itimes` is installed in `ext2fs_ufsops` and reached through `EXT2FS_ITIMES`/UFS update paths.

Notable behavior:
- `ext2fs_itimes` updates ctime for `IN_CHANGE` or `IN_MODIFY`, and mtime for `IN_UPDATE` or `IN_MODIFY`.
- It uses ext2 inode size when writing timestamp fields, supporting larger ext2 inode layouts.
