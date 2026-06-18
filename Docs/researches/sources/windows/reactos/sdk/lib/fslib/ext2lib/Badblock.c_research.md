# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Badblock.c

Read completely: 43 lines.

This ext2 formatting helper creates the reserved bad-block inode. `create_bad_block_inode` marks `EXT2_BAD_INO` allocated in the inode bitmap, decrements free inode counts in group 0 and the superblock, initializes an `EXT2_INODE` with mode derived from `0777 & ~umask`, two links, zero size/blocks, and current timestamps, then saves it with `ext2_save_inode`.

The `bb_list` argument is currently unused; no listed bad blocks are attached to the inode.

Security/reliability notes: this assumes the inode bitmap and group descriptors are already initialized and that free inode counts are nonzero. The unused bad-block list means bad block recording is incomplete.
