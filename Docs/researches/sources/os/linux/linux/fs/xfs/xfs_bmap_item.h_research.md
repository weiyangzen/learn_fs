# File Research: sources/os/linux/linux/fs/xfs/xfs_bmap_item.h

Defines kernel-only BUI/BUD structures and APIs for deferred bmap btree redo logging.

Key elements:
- Documents BUI as bmap update intent and BUD as bmap update done.
- Defines `XFS_BUI_MAX_FAST_EXTENTS` as one.
- `struct xfs_bui_log_item` contains log item, refcount, next extent counter, and BUI format.
- `xfs_bui_log_item_sizeof` computes variable-size item allocation size.
- `struct xfs_bud_log_item` contains done log item, pointer to BUI, and BUD format.
- Declares BUI/BUD caches, `xfs_bmap_defer_add`, and log-space calculators.

Dependencies:
- Implemented by `xfs_bmap_item.c`.
- Uses format definitions from XFS log format headers.

Research notes:
- Comments explicitly describe crash recovery semantics: intent in the first transaction, done item in the transaction that performs the bmbt update.
