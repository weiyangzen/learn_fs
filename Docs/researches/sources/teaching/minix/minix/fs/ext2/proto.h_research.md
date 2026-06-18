# File Research: sources/teaching/minix/minix/fs/ext2/proto.h

This header declares ext2 server function prototypes and aliases `put_block` to `lmfs_put_block`.

Coverage:
- Allocation: block and inode alloc/free.
- Inode cache and disk I/O.
- Link/unlink/rename/truncate.
- Sync, mount, create, directory lookup, chmod/chown.
- Read/write/getdents and block mapping.
- Superblock/group descriptor operations.
- Utility functions for endian conversion, string comparison, bitmap mutation.
- Write-side block mapping helpers.

Role:
- Provides cross-module API boundaries for the ext2 server.
- Shows the fsdriver-facing surface implemented across the ext2 `.c` files.
