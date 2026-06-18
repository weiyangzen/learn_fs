# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/orphan.c

Implements ext4 orphan file creation, truncation, sizing, and checksum helpers. The orphan file is a bounded regular file containing orphan inode slots and per-block tails.

`ext2fs_create_orphan_file()` allocates or reuses the configured orphan inode, optionally truncates an existing non-empty orphan file, allocates up to `EXT4_MAX_ORPHAN_FILE_BLOCKS`, writes initialized blocks, sets timestamps/mode/link count/size, and sets the orphan_file feature.

Checksum helpers compute CRC32C over orphan inode number, generation, block number, and block payload. Metadata checksum mode writes and verifies the orphan block tail checksum.

`ext2fs_truncate_orphan_file()` punches all blocks from the orphan file, clears the inode, clears orphan-related superblock features, marks the superblock dirty, and clears `EXT2_FLAG_SUPER_ONLY` because descriptors/accounting may need updates.
