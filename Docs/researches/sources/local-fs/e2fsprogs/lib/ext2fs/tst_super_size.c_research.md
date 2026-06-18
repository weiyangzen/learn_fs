# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_super_size.c

Validates the exact field layout of `struct ext2_super_block`. Under GCC 4 or newer, it checks field sizes and offsets in order and exits on mismatch.

The checked fields cover legacy ext2 superblock data, journal metadata, ext4 64-bit fields, MMP, RAID layout, snapshot fields, error tracking, mount options, quota inode numbers, encryption metadata, checksum seed, high timestamp bytes, encoding fields, orphan-file inode, reserved space, and final checksum. It verifies the final superblock size reaches 1024 bytes.
