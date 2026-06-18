# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/swapfs.c

Contains endian-swapping routines for ext2/ext3/ext4 on-disk structures. Major entry points include `ext2fs_swap_super`, `ext2fs_swap_group_desc2`, `ext2fs_swap_group_desc`, `ext2fs_swap_inode_full`, `ext2fs_swap_inode`, `ext2fs_swap_mmp`, and directory-entry swab helpers.

The superblock swap covers legacy and modern fields including 64-bit block counts, MMP, snapshot, quota, metadata checksum, encoding, and orphan-file fields. Build-time assertions are used to catch reserved-field layout drift. Group descriptor swapping handles 32-bit descriptors and 64-bit descriptor extensions depending on filesystem descriptor size.

Inode swapping is careful about in-place conversion: it determines symlink/extent/inline-data state before or after byte swapping depending on direction. Extent and inline-data payloads in `i_block` are intentionally not swapped here because they are swapped on access. Extended attributes inside large inodes are also swapped when present.

Directory entry swabbing validates record lengths and name lengths unless `EXT2_FLAG_IGNORE_SWAP_DIRENT` is set. The output path returns corruption for malformed directory records.
