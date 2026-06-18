# File Research: sources/os/linux/linux/fs/nilfs2/gcinode.c

This file implements dummy inodes used by NILFS2 garbage collection to cache blocks that are being moved.

Purpose:
- GC inodes hold data and node buffers for blocks selected by the cleaner.
- These buffers are separate from normal dirty data of the current generation, avoiding overlap between live new-generation writes and blocks being moved from older segments.

Data block reads:
- `nilfs_gccache_submit_read_data()` registers a data buffer in a GC inode page cache using a dummy offset key.
- If no physical block number is supplied, it translates the virtual block number through DAT.
- It submits the read and stores `vbn` in `b_blocknr` when present, otherwise the physical number.

Node block reads:
- `nilfs_gccache_submit_read_node()` uses the associated btnode cache and `nilfs_btnode_submit_block()`.
- It treats btnode cache-hit internal `-EEXIST` as success.

Validation and dirtying:
- `nilfs_gccache_wait_and_mark_dirty()` waits for read completion, checks uptodate state, validates node buffers with `nilfs_btree_broken_node_block()`, rejects already-dirty buffers with `-EEXIST`, and marks valid buffers dirty.

GC inode setup and cleanup:
- `nilfs_init_gcinode()` initializes a GC inode as regular buffer-cache storage, initializes GC bmap ops, and attaches a B-tree node cache.
- `nilfs_remove_all_gcinodes()` walks the NILFS GC inode list, removes each inode, truncates data pages, clears btnode cache pages, and drops inode references.

Important invariants:
- GC block staging is serialized by ioctl-level GC coordination.
- Dirty GC buffers represent blocks to be written into a new log.
- Node blocks are validated before being marked dirty for relocation.
