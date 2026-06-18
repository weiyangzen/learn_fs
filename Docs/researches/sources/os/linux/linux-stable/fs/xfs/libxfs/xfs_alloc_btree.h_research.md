# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_alloc_btree.h

## Purpose

This header defines on-disk free-space btree layout helpers and declares BNOBT/CNTBT cursor and geometry APIs.

## Layout Macros

- `XFS_ALLOC_BLOCK_LEN(mp)`
  - Chooses CRC or non-CRC short btree block header length.
- `XFS_ALLOC_REC_ADDR`
  - Computes record address in a free-space btree block.
- `XFS_ALLOC_KEY_ADDR`
  - Computes key address in an internal free-space btree block.
- `XFS_ALLOC_PTR_ADDR`
  - Computes pointer address in an internal free-space btree block.

These macros account for header size and are also used by userspace tooling.

## Declared API

- Cursor constructors:
  - `xfs_bnobt_init_cursor`
  - `xfs_cntbt_init_cursor`
- Geometry:
  - `xfs_allocbt_maxrecs`
  - `xfs_allocbt_calc_size`
  - `xfs_allocbt_maxlevels_ondisk`
- Staged btree support:
  - `xfs_allocbt_commit_staged_btree`
- Cursor cache lifecycle:
  - `xfs_allocbt_init_cur_cache`
  - `xfs_allocbt_destroy_cur_cache`

## Important Invariants

- The btree block header size depends on the filesystem CRC feature.
- Record, key, and pointer indexes are 1-based, matching XFS btree conventions.
- Pointer address calculation depends on maximum records per block because internal blocks store all keys before pointers.

## Research Notes

This header is the structural bridge between raw free-space btree blocks and the generic btree/allocator code. It is small, but incorrect address macros would corrupt every BNOBT/CNTBT traversal or mutation.
