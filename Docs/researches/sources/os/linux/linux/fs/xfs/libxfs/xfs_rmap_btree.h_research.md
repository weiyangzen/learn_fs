# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rmap_btree.h

Header for reverse mapping btree layout and exported btree helpers.

Key contents:
- Defines `XFS_RMAP_BLOCK_LEN` as the v5 short btree block header length.
- Provides address macros for records, low keys, high keys, and pointers:
  `XFS_RMAP_REC_ADDR`, `XFS_RMAP_KEY_ADDR`, `XFS_RMAP_HIGH_KEY_ADDR`, `XFS_RMAP_PTR_ADDR`.
- Declares AG rmap cursor creation, staged commit, max-record/max-level calculations, size/reserve helpers, and cursor cache lifecycle.
- Declares optional in-memory rmap btree cursor/init functions.

Design notes:
- Rmap internal blocks store low and high keys per pointer due to overlapping physical ranges.
- Some macros are preserved for userspace tooling.
