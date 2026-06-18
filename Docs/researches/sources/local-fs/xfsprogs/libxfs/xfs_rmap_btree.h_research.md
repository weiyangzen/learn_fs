# File Research: sources/local-fs/xfsprogs/libxfs/xfs_rmap_btree.h

Header for rmap btree layout macros and btree management declarations.

Main contents:
- Defines `XFS_RMAP_BLOCK_LEN` as the v5 short btree CRC header length.
- Provides block address macros for records, low keys, high keys, and pointers:
  `XFS_RMAP_REC_ADDR`, `XFS_RMAP_KEY_ADDR`, `XFS_RMAP_HIGH_KEY_ADDR`, `XFS_RMAP_PTR_ADDR`.
- Declares AG cursor creation via `xfs_rmapbt_init_cursor`.
- Declares staged root commit, max record calculation, maxlevel computation, size calculation, max size, and reserve calculation helpers.
- Declares cursor cache lifecycle functions.
- Declares optional in-memory rmap btree cursor/init APIs through `xfs_rmapbt_mem_cursor` and `xfs_rmapbt_mem_init`.

Role:
- Exposes the overlapping rmap btree adapter to rmap update code, repair/staging code, and userspace libxfs consumers.
