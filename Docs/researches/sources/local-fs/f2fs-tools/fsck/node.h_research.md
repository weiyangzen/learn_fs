# File Research: sources/local-fs/f2fs-tools/fsck/node.h

Purpose: defines inline node/inode addressing helpers and traversal mode constants for F2FS fsck tooling.

Key contents:
- `IS_INODE()` identifies inode nodes by footer `nid == ino`.
- `ADDRS_PER_PAGE()` returns inode or node address capacity; for non-inode nodes it can read the owning inode to account for extra inode layout.
- `blkaddr_in_inode()`, `blkaddr_in_node()`, and `datablock_addr()` abstract address array access.
- `set_nid()` and `get_nid()` update inode child NID fields or indirect-node NID arrays.
- Defines dnode traversal modes: `ALLOC_NODE`, `LOOKUP_NODE`, `LOOKUP_NODE_RA`.
- `set_new_dnode()` initializes `struct dnode_of_data`.
- `inc_inode_blocks()` increments inode block count and marks inode dirty.
- `IS_DNODE()` distinguishes direct data nodes from indirect nodes based on node offset layout.
- Footer helpers return inode number, checkpoint version, next block address, fsync/dentry bits, and recoverability based on checkpoint CRC flags.
- `set_cold_node()` toggles the cold-node flag based on directory status.

Important dependencies:
- Included by `node.c`, `inject.c`, `quotaio.h`, and `mount.c`.
- Depends on `fsck.h` and F2FS layout macros.

Risk notes:
- Several helpers assume valid node pages and assert on allocation/read failure.
- `ADDRS_PER_PAGE()` can allocate and read an inode block when the caller does not provide one, so it is not a pure accessor.
