# File Research: sources/local-fs/xfsprogs/libxfs/xfs_refcount_btree.h

Header for refcount btree on-disk block layout helpers and public btree management APIs.

Main contents:
- Defines `XFS_REFCOUNT_BLOCK_LEN` as the v5 short btree CRC header length.
- Provides address macros for records, keys, and pointers inside a refcount btree block:
  `XFS_REFCOUNT_REC_ADDR`, `XFS_REFCOUNT_KEY_ADDR`, `XFS_REFCOUNT_PTR_ADDR`.
- Declares cursor creation through `xfs_refcountbt_init_cursor`.
- Declares geometry helpers `xfs_refcountbt_maxrecs`, `xfs_refcountbt_compute_maxlevels`, and `xfs_refcountbt_maxlevels_ondisk`.
- Declares sizing/reservation helpers `xfs_refcountbt_calc_size`, `xfs_refcountbt_max_size`, and `xfs_refcountbt_calc_reserves`.
- Declares staged btree commit and cursor cache lifecycle functions.

Role:
- This file exposes the btree adapter defined in `xfs_refcount_btree.c` to refcount update code, repair/build code, and userspace libxfs consumers.
