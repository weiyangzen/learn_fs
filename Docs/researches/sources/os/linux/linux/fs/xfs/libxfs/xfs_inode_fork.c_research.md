# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_fork.c

This file converts inode fork data between on-disk representation and in-core fork state, manages fork memory, flushes fork contents back to dinodes, and provides helpers for COW forks and extent-count limits.

Major responsibilities:
- Initialize local-format forks with optional symlink NUL termination.
- Format data forks from disk via `xfs_iformat_data_fork`.
- Format attr forks from disk via `xfs_iformat_attr_fork`.
- Decode local, extent, regular btree, and metadata-btree fork formats.
- Allocate/reallocate btree roots with `xfs_broot_alloc` and `xfs_broot_realloc`.
- Resize inline data with `xfs_idata_realloc`.
- Destroy fork memory with `xfs_idestroy_fork`.
- Copy in-core extents to disk records with `xfs_iextents_copy`.
- Flush fork state into a dinode with `xfs_iflush_fork`.
- Initialize COW forks with `xfs_ifork_init_cow`.
- Verify local data and attr fork contents.
- Upgrade or reject extent counts through `xfs_iext_count_extend`.
- Decide realtime mapping behavior with `xfs_ifork_is_realtime`.

Important behavior:
- Extent-format forks are loaded into the in-core extent tree from `xfs_iext_tree.c`.
- Btree-format forks copy only the root initially; full extent loading can be deferred.
- `if_needextents` is stored with release semantics so readers can acquire it and safely observe fork format.
- Local data verifiers delegate to directory shortform, symlink shortform, and attr shortform validators.
- Metadata-btree forks dispatch to realtime rmap/refcount formatters and flushers based on inode metatype.

Risk notes:
- Fork format dispatch is mode-sensitive and corruption-sensitive.
- Delayed extent loading requires memory-ordering discipline.
- `xfs_iextents_copy` skips delayed/null-startblock extents and asserts physical extent validity before writing disk records.
