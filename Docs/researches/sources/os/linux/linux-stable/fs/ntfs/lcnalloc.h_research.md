# File Research: sources/os/linux/linux-stable/fs/ntfs/lcnalloc.h

## Summary
Declares NTFS cluster allocation/deallocation interfaces and zone identifiers.

## Main Contents
- Zone constants `MFT_ZONE` and `DATA_ZONE`, with boundary sentinels.
- `ntfs_cluster_alloc()` for bitmap-backed cluster allocation.
- `__ntfs_cluster_free()` and inline `ntfs_cluster_free()` for freeing clusters from an inode runlist.
- `ntfs_cluster_free_from_rl_nolock()` and inline `ntfs_cluster_free_from_rl()` for freeing all real clusters in a runlist.

## Important Details
The header documents lock requirements for deallocation in detail. `ntfs_cluster_free()` requires the inode runlist write lock and may map missing runlist fragments. `ntfs_cluster_free_from_rl()` saves NOFS allocation context, takes `vol->lcnbmp_lock`, calls the nolock helper, then restores context.

## Risks
Callers must not assume `ntfs_cluster_free()` edits the runlist; it only updates the LCN bitmap and accounting, leaving runlist removal or sparse marking to the caller. If a search context is passed, its saved pointers may point to new memory after the call and must be refreshed.
