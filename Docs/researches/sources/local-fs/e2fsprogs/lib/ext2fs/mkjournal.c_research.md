# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/mkjournal.c

Creates journal superblocks, journal files, journal inodes, and external journal links. Main public functions include `ext2fs_create_journal_superblock2`, `ext2fs_zero_blocks2`, `ext2fs_get_journal_params`, `ext2fs_add_journal_device`, and `ext2fs_add_journal_inode3`.

Journal superblocks are initialized with JBD2 magic, block size, max length including fast-commit blocks, UUID, sequence, and external-journal offsets when needed. Journal sizing uses filesystem block count with bounds and splits fast-commit space when enabled.

Mounted filesystems use POSIX `.journal` file creation and disable lazy initialization because writes allocate blocks. Unmounted filesystems allocate `EXT2_JOURNAL_INO` directly with `ext2fs_fallocate`, write the journal superblock, and back up journal block mapping in the superblock.

Risk points: mounted journal creation relies on mount detection, file flags/ioctls, and host filesystem behavior; `ext2fs_zero_blocks2` uses a static reusable zero buffer; external journal setup validates block device type, JBD2 superblock magic/type, block size, and user UUID slots.
