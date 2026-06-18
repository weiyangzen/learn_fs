# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_bswap.c

Provides big-endian byte-swap helpers for ext2 metadata, which is little-endian on disk. On little-endian systems these helpers are not built because header macros use `memcpy`.

For big-endian builds, `e2fs_sb_bswap` copies the superblock then swaps selected superblock fields, `e2fs_cg_bswap` swaps group descriptor arrays, and `e2fs_i_bswap` swaps dinode fields and copies block pointers. The dinode helper only swaps extra inode size if the filesystem inode size exceeds the rev0 size; it does not fully swap every ext4 extra timestamp/checksum field.
