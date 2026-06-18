# File Research: sources/local-fs/jfsutils/libfs/jfs_endian.c

## Purpose
Implements byte-swapping for JFS on-disk and fsck workspace structures on big-endian hosts. The file is compiled effectively only under `__BYTE_ORDER == __BIG_ENDIAN`.

## Swap Coverage
Provides swap routines for:
- Allocation maps: `ujfs_swap_dbmap`, `ujfs_swap_dmap`, `ujfs_swap_dmapctl`.
- Inodes and inode maps: `ujfs_swap_dinode`, `ujfs_swap_dinomap`, `ujfs_swap_iag`.
- Trees: `ujfs_swap_dtpage_t`, `ujfs_swap_xtpage_t`.
- Fsck workspace/log records: `ujfs_swap_fsck_blk_map_hdr`, `ujfs_swap_fsck_blk_map_page`, `ujfs_swap_fscklog_entry_hdr`.
- Journal structures: `ujfs_swap_logpage`, `ujfs_swap_logsuper`, `ujfs_swap_lrd`.
- Superblock: `ujfs_swap_superblock`.

## Important Logic
- `ujfs_swap_dinode()` swaps scalar inode fields and then conditionally swaps dtree or xtree roots based on `di_mode`; directory index support depends on `JFS_DIR_INDEX`.
- `ujfs_swap_dtpage_t()` walks directory entries and continuation slots, guarding against out-of-page slot indexes.
- `ujfs_swap_lrd()` switches on log record type and swaps only the relevant union fields.

## Dependencies
Includes `jfs_endian.h`, `devices.h`, and underlying JFS format headers through `jfs_endian.h`.

## Notes
The routines use little-endian conversion helpers because JFS disk structures are little-endian. On little-endian hosts these functions are compiled out and mapped to no-ops by the header.
