# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_ialloc_btree.h

## Purpose

`xfs_ialloc_btree.h` declares inode allocation btree cursor APIs, block layout macros, record access macros, sparse record helpers, reserve calculations, staged btree commit, max-level calculation, and cursor cache lifecycle.

## Main Content

- Defines `XFS_INOBT_BLOCK_LEN(mp)`:
  - Chooses CRC or non-CRC short btree block header size.
- Defines on-block address macros:
  - `XFS_INOBT_REC_ADDR`.
  - `XFS_INOBT_KEY_ADDR`.
  - `XFS_INOBT_PTR_ADDR`.
- Declares cursor constructors:
  - `xfs_inobt_init_cursor`.
  - `xfs_finobt_init_cursor`.
- Declares geometry helpers:
  - `xfs_inobt_maxrecs`.
  - `xfs_iallocbt_calc_size`.
  - `xfs_iallocbt_maxlevels_ondisk`.
- Declares sparse inode conversion:
  - `xfs_inobt_irec_to_allocmask`.
  - `xfs_inobt_rec_check_count` in debug/warn builds, otherwise a zero-return macro.
- Declares finobt reservation calculation:
  - `xfs_finobt_calc_reserves`.
- Declares staged btree commit:
  - `xfs_inobt_commit_staged_btree`.
- Declares cursor cache lifecycle:
  - `xfs_inobt_init_cur_cache`.
  - `xfs_inobt_destroy_cur_cache`.

## Key Interfaces and Invariants

- Record/key/pointer address macros use one-based btree indices, matching XFS btree conventions.
- The same physical record format is used by inobt and finobt.
- Header length depends on the filesystem CRC feature and must be used instead of raw structure sizes.
- Some macros may appear unused in kernel code but are kept for userspace libxfs consumers.

## Dependencies

Depends on btree block constants from `xfs_format.h`, mount feature predicates, and inode record types. Implemented by `xfs_ialloc_btree.c`.
