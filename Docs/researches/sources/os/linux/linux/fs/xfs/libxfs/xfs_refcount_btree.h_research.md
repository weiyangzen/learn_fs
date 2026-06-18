# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_refcount_btree.h

Header for AG refcount btree layout and exported btree helpers.

Key contents:
- Defines `XFS_REFCOUNT_BLOCK_LEN` as the v5 short btree block header length.
- Provides address macros for records, keys, and pointers inside refcount btree blocks:
  `XFS_REFCOUNT_REC_ADDR`, `XFS_REFCOUNT_KEY_ADDR`, `XFS_REFCOUNT_PTR_ADDR`.
- Declares cursor initialization, max-record calculation, max-level computation, size/reserve helpers, staged btree commit, and cursor cache lifecycle.

Design notes:
- Address macros are kept for both kernel and userspace consumers.
- The header intentionally exposes only btree-structure helpers; record mutation semantics are in `xfs_refcount.h/.c`.
