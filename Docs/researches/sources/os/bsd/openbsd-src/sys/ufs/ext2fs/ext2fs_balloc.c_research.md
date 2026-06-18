# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_balloc.c

Allocates physical storage for a file logical block. `ext2fs_buf_alloc` handles direct blocks first: if present it reads the block; if absent it chooses a preference, allocates a block, records it in `i_e2fs_blocks`, marks inode change/update, gets a buffer, sets disk block number, and optionally clears it.

For indirect blocks it uses `ufs_getlbns`, allocates missing indirect blocks synchronously so metadata never points at garbage, wires the chain, and then allocates or returns the requested data block. On failure it frees newly allocated blocks, unwinds indirect pointers, invalidates cached indirect buffers, and adjusts block accounting. This file only handles classic block maps, not ext4 extent-tree allocation.
