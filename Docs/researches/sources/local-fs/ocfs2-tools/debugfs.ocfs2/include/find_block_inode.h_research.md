# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/find_block_inode.h

## Role

This header declares the block-owner reverse lookup function used by `icheck`.

## API

`find_block_inode(ocfs2_filesys *fs, uint64_t *blkno, int count, FILE *out)` accepts a filesystem handle, an array of queried block numbers, a count, and output stream.

## Implementation

The function is implemented in `find_block_inode.c`.
