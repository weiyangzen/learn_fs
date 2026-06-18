# File Research: sources/local-fs/ocfs2-tools/libocfs2/cached_inode.c

Small cached-inode lifecycle helper module.

`ocfs2_read_cached_inode()` validates block number bounds, allocates an `ocfs2_cached_inode`, allocates a block buffer for the dinode, reads the inode, and returns the populated cache object. `ocfs2_free_cached_inode()` frees any loaded chain bitmap, inode buffer, and wrapper. `ocfs2_write_cached_inode()` requires a read-write filesystem, validates bounds, and writes the cached dinode. `ocfs2_refresh_cached_inode()` discards loaded chain allocator bitmap state and rereads the dinode into the existing buffer.

This module is foundational for allocators, directory scan, quota flushing, and any code that needs inode plus lazily attached chain bitmap state.
