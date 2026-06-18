# File Research: sources/os/linux/linux/fs/xfs/xfs_rmap_item.h

## Role

Header for reverse mapping update intent/done log items.

## Main Contents

- Documents RUI/RUD redo semantics for map, unmap, and convert rmapbt updates across rolled transactions.
- `XFS_RUI_MAX_FAST_EXTENTS`: fast allocation threshold of 16 extents.
- `struct xfs_rui_log_item`: log item, reference count, next extent counter, and variable RUI format payload.
- `xfs_rui_log_item_sizeof`: computes dynamic RUI allocation size.
- `struct xfs_rud_log_item`: done log item linking to original RUI plus RUD format.
- Extern declarations for RUI/RUD slab caches.
- Declaration for `xfs_rmap_defer_add`.
- Log space helpers `xfs_rui_log_space` and `xfs_rud_log_space`.

## Dependencies

Forward declares mount, slab cache, and rmap intent types. Implemented by `xfs_rmap_item.c`.
