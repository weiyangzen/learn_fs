# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_alloc_btree.h

Declares XFS free-space btree layout macros and cursor/utility APIs.

Key behavior:
- Defines `XFS_ALLOC_BLOCK_LEN(mp)`, selecting CRC or non-CRC short btree block header length.
- Defines record, key, and pointer address macros for allocation btree blocks:
  - `XFS_ALLOC_REC_ADDR`.
  - `XFS_ALLOC_KEY_ADDR`.
  - `XFS_ALLOC_PTR_ADDR`.
- Declares bnobt and cntbt cursor constructors.
- Declares max-record calculation for alloc btree blocks.
- Declares allocation btree size estimation.
- Declares staged btree root commit for rebuild/repair.
- Declares maximum on-disk alloc btree height calculation.
- Declares cursor cache lifecycle functions.

Important interactions:
- Used by allocator code, AG header initialization, userspace/libxfs consumers, and online repair staging code.
