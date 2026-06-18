# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_iscan.c

Tests inode table scanning behavior in the presence of bad blocks. It creates a synthetic filesystem with `test_io_manager`, allocates inode tables and bitmaps, installs read callbacks that record every block touched, and marks a fixed list of bad inode-table blocks.

During `ext2fs_get_next_inode` iteration, `EXT2_ET_BAD_BLOCK_IN_INODE_TABLE` marks the affected inode in `bad_inode_map`. After scanning, it verifies no bad block was read, no inode-table block was missed, and no block was read twice. It prints touched ranges and bad inodes, returning failure count.
