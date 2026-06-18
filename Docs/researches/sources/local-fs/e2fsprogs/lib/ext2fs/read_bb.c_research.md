# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/read_bb.c

Reads bad blocks from the filesystem’s bad block inode (`EXT2_BAD_INO`). `ext2fs_read_bb_inode()` creates a badblocks list if needed, sizes it from inode block count with clamps, and iterates the inode’s blocks read-only.

The callback ignores metadata/indirect entries (`blockcnt < 0`) and out-of-filesystem block numbers, adding only valid blocks to the badblocks list.

This function converts on-disk bad block inode mappings into libext2fs badblocks-list form for tools such as fsck and mkfs workflows.
