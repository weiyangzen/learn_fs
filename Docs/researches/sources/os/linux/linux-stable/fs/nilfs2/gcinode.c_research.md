# File Research: sources/os/linux/linux-stable/fs/nilfs2/gcinode.c

## Summary
Implements dummy garbage-collection inodes used to cache data and node blocks that will be moved into a new NILFS log.

## Main Responsibilities
- Reads GC data blocks into a dummy inode page cache.
- Reads GC B-tree node blocks into the associated node cache.
- Waits for GC reads and marks buffers dirty for copying.
- Initializes GC inode state and bmap operations.
- Removes all queued GC inodes after cleaning.

## Important Behavior
Data reads use `nilfs_gccache_submit_read_data()`, keyed by a dummy offset, with `b_blocknr` set to the physical block for I/O and restored to the virtual block number when provided. If the physical block is omitted, DAT translation supplies it.

Node reads use `nilfs_btnode_submit_block()` against the GC inode's associated B-tree node cache. Cache-hit `-EEXIST` is normalized to success.

`nilfs_gccache_wait_and_mark_dirty()` waits for I/O completion, validates uptodate state, checks B-tree node integrity for node buffers, returns `-EEXIST` for already-dirty buffers, and otherwise marks the buffer dirty so segment construction will copy it.

`nilfs_remove_all_gcinodes()` drains `ns_gc_inodes`, truncates data and node caches, and drops inode references after each GC run.

## Risks
GC block movement relies on no overlap between current-generation dirty blocks and blocks being moved. Buffer association lists are used as temporary GC ownership markers, so conflicting list membership is treated as a serious conflict by ioctl code.
