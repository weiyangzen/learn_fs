# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass5.c

Implements ext2 fsck phase 5: bitmap and summary information verification.

For each block group:
- Reconstructs an inode bitmap from `statemap`.
- Reconstructs a block bitmap from `blockmap` and filesystem size bounds.
- Counts free blocks, free inodes, and directories.
- Marks reserved/invalid inode slots used in the reconstructed inode map.
- Compares reconstructed counts with group descriptor counts.
- Compares reconstructed block and inode bitmaps with on-disk bitmaps.
- Repairs mismatched group summaries and bitmaps when `dofix` approves.

After all groups:
- Accumulates global free block and inode counts.
- Compares them with superblock summary fields.
- Repairs superblock free block/inode totals when approved.

Includes `print_bmap` for debug dumping bitmap byte arrays.
