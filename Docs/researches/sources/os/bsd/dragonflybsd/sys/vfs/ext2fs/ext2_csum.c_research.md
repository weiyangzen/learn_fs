# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_csum.c

This file implements checksum support for ext2/ext3/ext4 metadata structures used by the DragonFlyBSD ext2 driver: superblocks, directory blocks, htree nodes, extent blocks, group bitmaps, inodes, and group descriptors.

Key responsibilities:
- Establish the CRC32C seed from `csum_seed` or filesystem UUID.
- Verify and set superblock checksums.
- Detect and initialize directory checksum tails.
- Verify/set directory entry block and htree index checksums.
- Verify/set extent block checksums.
- Verify/set block and inode bitmap checksums stored in group descriptors.
- Verify/set inode checksums, including high checksum words when supported by `extra_isize`.
- Verify/set group descriptor checksums using CRC32C for metadata checksums or CRC16 for older `GDT_CSUM`.

Important functions:
- `ext2_sb_csum_set_seed`, `ext2_sb_csum_verify`, `ext2_sb_csum_set`: Superblock checksum seed and checksum maintenance.
- `ext2_init_dirent_tail`, `ext2_is_dirent_tail`, `ext2_dirent_get_tail`: Directory checksum tail helpers.
- `ext2_dirent_csum_verify` / `ext2_dirent_csum_set`: Directory block checksum handling using inode number and generation.
- `ext2_dx_csum_verify` / `ext2_dx_csum_set`: HTree root/node checksum handling.
- `ext2_dir_blk_csum_verify`: Dispatches a directory buffer to dirent-tail or htree checksum verification.
- `ext2_extent_blk_csum_verify` / `ext2_extent_blk_csum_set`: Extent block checksum handling.
- `ext2_gd_i_bitmap_csum_*` and `ext2_gd_b_bitmap_csum_*`: Bitmap checksum verification and update.
- `ext2_ei_csum_verify` / `ext2_ei_csum_set`: Inode checksum verification/update, with zeroed new inodes accepted.
- `ext2_gd_csum_verify` / `ext2_gd_csum_set`: Group descriptor checksum handling.

Important interactions:
- Called by allocation/free paths before and after bitmap modification.
- Called by `ext2_blkatoff`, lookup, and htree write paths for directory block validation/update.
- Called by inode conversion/update paths to validate and write dinode checksums.

Notable behavior and risks:
- Metadata checksums are silently bypassed when the feature bit is absent.
- Directory block verification treats either a dirent tail or an htree count structure as the checksum-bearing format.
- Superblock checksum verification rejects unsupported checksum types.
