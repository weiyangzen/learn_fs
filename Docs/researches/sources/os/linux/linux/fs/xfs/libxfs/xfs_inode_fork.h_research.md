# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_fork.h

This header defines the in-core inode fork structure and the public API for fork formatting, extent-tree manipulation, and fork helpers.

Key contents:
- `struct xfs_ifork`, containing:
  - inline data or extent-tree root in `if_data`
  - in-core btree root in `if_broot`
  - extent count, fork format, fork height, sequence counter, and delayed extent-read flag
- Worst-case extent-count growth constants for write, punch, xattr, reflink COW, and swap/rmap operations.
- Helpers for fork format, extent counts, max extent counts, and on-disk extent counter extraction.
- APIs for:
  - formatting data/attr forks
  - flushing forks
  - destroying/reallocating fork data
  - btree-root allocation
  - extent tree insert/remove/update/lookup/traversal
  - COW fork initialization
  - local fork verification
  - extent-count extension
  - realtime fork checks
- Cursor helper wrappers and `for_each_xfs_iext`.

Important invariants:
- Data/COW and attr forks have different small/large extent-count maxima.
- `xfs_need_iread_extents` uses acquire semantics matching release stores during fork formatting.
- `xfs_ifork_nextents(NULL)` returns zero and `xfs_ifork_format(NULL)` defaults to extents, simplifying absent attr/COW fork handling.

Integration:
- Central declaration point for extent tree code, inode fork conversion, bmap, writeback, and attr handling.

Risk notes:
- Constants here feed reservation and extent-count admission checks; incorrect counts can cause `-EFBIG` failures or overflows.
- The fork structure is heavily shared; layout or semantic changes have broad effects.
