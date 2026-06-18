# File Research: sources/local-fs/jfsutils/libfs/inode.c

## Purpose
Implements low-level read/write access to JFS aggregate and fileset inodes, plus xtree logical-block-to-disk-offset lookup.

## Main Functions
- `ujfs_rwinode(FILE *fp, struct dinode *di, uint32_t inum, int32_t mode, int32_t fs_block_size, uint32_t which_table, uint32_t sb_flag)`: reads or writes an aggregate/fileset inode.
- `ujfs_rwdaddr(FILE *fp, int64_t *offset, struct dinode *di, int64_t lbno, int32_t mode, int32_t fs_block_size)`: resolves an inode logical block number through the inode xtree to a byte offset.

## Inode Access Logic
- Aggregate inode table reads are direct offsets from `AGGR_INODE_TABLE_START`, with a range check against `NUM_INODE_PER_EXTENT`.
- Fileset inode reads first read the fileset inode allocation map inode, use `ujfs_rwdaddr()` to locate the target IAG, read the IAG, then compute the inode extent address from `iag.inoext[]`.

## Xtree Traversal
`ujfs_rwdaddr()` binary-searches xtree entries, descends through internal pages with `ujfs_rw_diskblocks()`, swaps pages on big-endian builds, and returns the computed byte offset for leaf hits.

## Dependencies
Uses JFS inode/imap/filsys definitions, `devices.h`, endian helpers, `utilsubs.h`, and message/error constants.

## Notes
The bottom of `ujfs_rwdaddr()` contains unreachable legacy code after an unconditional “not found” return; the active implementation is the xtree traversal above it.
