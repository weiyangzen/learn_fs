# File Research: sources/os/linux/linux/fs/xfs/xfs_refcount_item.h

## Role

Header for refcount update intent/done log items.

## Main Contents

- Documents CUI/CUD redo semantics for refcount btree updates across rolled transactions.
- `XFS_CUI_MAX_FAST_EXTENTS`: fast allocation threshold of 16 extents.
- `struct xfs_cui_log_item`: log item, reference count, next extent counter, and variable CUI format payload.
- `xfs_cui_log_item_sizeof`: computes dynamic CUI allocation size.
- `struct xfs_cud_log_item`: done log item linking to the original CUI plus CUD format.
- Extern declarations for CUI/CUD slab caches.
- Declaration for `xfs_refcount_defer_add`.
- Log space helpers `xfs_cui_log_space` and `xfs_cud_log_space`.

## Dependencies

Forward declares `xfs_mount`, `kmem_cache`, and `xfs_refcount_intent`. Implemented by `xfs_refcount_item.c` and consumed by refcount/reflink/defer/log code.
