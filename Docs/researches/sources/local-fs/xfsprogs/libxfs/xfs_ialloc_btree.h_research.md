# File Research: sources/local-fs/xfsprogs/libxfs/xfs_ialloc_btree.h

## Purpose
Declares inode allocation btree layout helpers, cursor constructors, record capacity helpers, sparse inode allocation mask conversion, finobt reserve calculation, staged commit, maximum-level calculation, and cursor cache lifecycle.

## Main Contents
- Header sizing:
  - `XFS_INOBT_BLOCK_LEN(mp)` chooses CRC or non-CRC short btree header length.
- Block layout access macros:
  - `XFS_INOBT_REC_ADDR`, `XFS_INOBT_KEY_ADDR`, and `XFS_INOBT_PTR_ADDR` compute record/key/pointer addresses within a btree block.
  - Comments note that some macros are used in userspace even if they appear unused.
- Cursor constructors:
  - `xfs_inobt_init_cursor` for inode allocation btree.
  - `xfs_finobt_init_cursor` for free inode btree.
- Capacity and sizing:
  - `xfs_inobt_maxrecs`.
  - `xfs_iallocbt_calc_size`.
  - `xfs_iallocbt_maxlevels_ondisk`.
- Sparse inode support:
  - `xfs_inobt_irec_to_allocmask`.
  - Debug/warn `xfs_inobt_rec_check_count`.
- Finobt and rebuild support:
  - `xfs_finobt_calc_reserves`.
  - `xfs_inobt_commit_staged_btree`.
- Cursor cache lifecycle:
  - `xfs_inobt_init_cur_cache`.
  - `xfs_inobt_destroy_cur_cache`.

## Dependencies and Integration
- Implemented by `xfs_ialloc_btree.c`.
- Used by inode allocation/freeing, scrub, repair, btree rebuild, and userspace tools that inspect btree block layouts.
- Depends on ondisk record/key/pointer types from `xfs_format.h`.

## Invariants
- Address macros use 1-based btree indexes consistent with XFS btree code.
- Header length must account for CRC feature state.
- Finobt and inobt use the same record shape but different roots and semantics.

## Notable Risks
- The address macros perform raw pointer arithmetic over ondisk buffers; wrong maxrecs/header inputs will misaddress records.
- Because userspace uses some macros directly, layout changes require broad compatibility review.
