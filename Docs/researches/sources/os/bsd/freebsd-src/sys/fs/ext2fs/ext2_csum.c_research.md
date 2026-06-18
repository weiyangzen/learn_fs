# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_csum.c

This file implements metadata checksum calculation, verification, and update for FreeBSD ext2/ext3/ext4 structures.

Key responsibilities:
- Establish the CRC32C seed from `csum_seed` or filesystem UUID.
- Verify and write superblock checksums.
- Verify and write external xattr block checksums.
- Detect, verify, initialize, and update directory entry checksum tails.
- Verify and update HTree node/root checksums.
- Verify and update extent block checksums.
- Verify and update block/inode bitmap checksums stored in group descriptors.
- Verify and write inode checksums and group descriptor checksums.

Important functions:
- `ext2_sb_csum_set_seed`, `ext2_sb_csum_verify`, `ext2_sb_csum_set`.
- `ext2_extattr_blk_csum_verify`, `ext2_extattr_blk_csum_set`.
- `ext2_init_dirent_tail`, `ext2_is_dirent_tail`, `ext2_dirent_get_tail`, `ext2_dirent_csum_verify`, `ext2_dirent_csum_set`.
- `ext2_dx_csum_verify`, `ext2_dx_csum_set`, `ext2_dir_blk_csum_verify`.
- `ext2_extent_blk_csum_verify`, `ext2_extent_blk_csum_set`.
- `ext2_gd_i_bitmap_csum_*`, `ext2_gd_b_bitmap_csum_*`, `ext2_ei_csum_*`, `ext2_gd_csum_*`.

Important interactions:
- Allocation/free paths call bitmap checksum functions.
- Directory lookup/update and htree mutation paths call directory/htree checksum functions.
- Inode conversion/update calls inode checksum functions.
- Extattr and extent implementations call their block checksum functions.

Notable behavior:
- Most checksum work is bypassed unless metadata checksum feature bits are present.
- Zeroed first-use inodes are accepted even when the computed inode checksum does not match.
