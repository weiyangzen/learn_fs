# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_mkfs.c

Filesystem creation support for ext2/ext3/ext4 images on an `ext4_blockdev`. It derives mkfs parameters, lays out block groups, writes superblocks/group descriptors/bitmaps, initializes reserved inodes, creates root and `lost+found`, and optionally creates an internal journal inode.

Key behavior:
- `sb2info` reads an existing superblock into `ext4_mkfs_info`.
- Computes default block size, blocks per group, inode count, inodes per group, journal size, group count, inode table blocks, descriptor blocks, and indirect block geometry.
- `fill_sb` constructs the in-memory ext superblock, including features, UUID, label, default hash seed/version, descriptor size, inode size preferences, and journal inode number.
- `write_bgroups` initializes group descriptors, block/inode bitmap blocks, inode table pointers, free counts, and uninitialized bitmap/table flags.
- `write_sblocks` writes backup superblocks for sparse-super groups and then writes the primary superblock at offset 1024.
- `alloc_inodes` allocates reserved inodes 1..11 and initializes root/journal inode block state where needed.
- `create_dirs` initializes root and `lost+found` directory contents with indexed-directory support when enabled.
- `create_journal_inode` allocates journal blocks and writes a JBD v2 superblock into the first journal data block.
- `ext4_mkfs` controls feature sets for ext2/ext3/ext4, disables unhandled features, enables optional journaling, initializes cache/writeback, formats, mounts internally, populates metadata, and tears down.

Notable dependencies:
- Uses allocation, directory, indexed-directory, inode, superblock, filesystem, block cache, and JBD type definitions from the local ext4srv modules.

Research notes:
- Feature masks are conservative: `meta_bg`, `flex_bg`, `64bit`, metadata checksums, group descriptor checksums, dir nlink, extra isize, and huge file are forcibly disabled during mkfs.
- `write_bgroups` computes `bg_start_block` with `first_data_block` added twice; for 1 KiB filesystems that likely shifts group metadata one block too far.
- The mkfs timestamps are initialized to zero rather than current time.
