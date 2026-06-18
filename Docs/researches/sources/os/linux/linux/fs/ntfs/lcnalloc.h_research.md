# File Research: sources/os/linux/linux/fs/ntfs/lcnalloc.h

This header declares NTFS cluster allocation and deallocation APIs plus the allocation zone identifiers.

Key definitions:
- Zone constants: `MFT_ZONE` and `DATA_ZONE`, bounded by `FIRST_ZONE` and `LAST_ZONE`.
- `ntfs_cluster_alloc()` allocates physical clusters and returns a runlist.
- `__ntfs_cluster_free()` is the lower-level free routine with rollback-mode support.
- `ntfs_cluster_free()` is the normal inline wrapper around `__ntfs_cluster_free(..., false)`.
- `ntfs_cluster_free_from_rl_nolock()` frees clusters from an already locked volume bitmap context.
- `ntfs_cluster_free_from_rl()` wraps the nolock variant with NOFS context and `vol->lcnbmp_lock`.

Important contract:
- `ntfs_cluster_free()` requires the target inode runlist to be write locked and the volume LCN bitmap lock to be unlocked on entry.
- The function may map unmapped runlist fragments using an attribute search context.
- It does not modify the caller’s runlist after freeing clusters; callers must later remove or mark freed runs.
- If a supplied search context becomes invalid, callers must check `IS_ERR(ctx->mrec)` and reinitialize or release the context.

Role in subsystem:
This header exposes the allocator/freeing contract to attribute, truncate, and metadata update code while centralizing locking expectations and rollback caveats.
