# File Research: sources/os/linux/linux/fs/xfs/xfs_filestream.c

Implements filestream allocation-group selection, which tries to keep related file allocations in a chosen AG to improve locality and reduce fragmentation.

Key logic:
- `struct xfs_fstrm_item` stores an MRU-cache association from parent inode to per-AG.
- `xfs_fstrm_free_func` drops the association, decrements the AG filestream count, releases the perag reference, and frees the item.
- `xfs_filestream_pick_ag` scans AGs from a starting AG looking for an unused/suitable AG with enough free extent length or minimum free blocks, tracking the AG with most free space as fallback. It uses `pagf_fstrms` as both suitability guard and active association count.
- `xfs_filestream_get_parent` uses dentry aliases to find the parent directory inode.
- `xfs_filestream_lookup_association` checks the MRU cache for an existing parent-to-AG association, validates free extent availability unless in low-space mode, and returns a referenced perag.
- `xfs_filestream_create_association` removes stale associations, chooses a starting AG, calls the picker, and inserts a new MRU cache item if allocation succeeds.
- `xfs_filestream_select_ag` is the allocator entry point: find parent, reuse association if sufficient, otherwise create a new one.
- `xfs_filestream_deassociate`, `xfs_filestream_mount`, and `xfs_filestream_unmount` manage MRU entries and mount lifecycle.

The file balances preferred locality with low-space fallbacks and metadata-preferred AG avoidance for user data.
