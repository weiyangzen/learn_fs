# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_inode.c

Read completely: 152 lines.

Implements generic UFS inode inactive and reclaim processing.

Core behavior:
- `ufs_inactive()` handles last-reference processing: ignores stale/zero-mode inodes, frees quota/inode resources and truncates data for unlinked writable inodes, clears mode/rdev, frees the on-disk inode through vtable dispatch, updates pending timestamps, unlocks the vnode, and recycles immediately when the inode is invalid.
- `ufs_reclaim()` stops lazy timestamp deferral, removes the inode from the global hash, purges namecache entries, releases the device vnode, frees optional dirhash state, and releases quota references.

Integration and risks:
- Deletion relies on `i_effnlink`/on-disk nlink state and mount read-only status.
- Reclaim intentionally does not free the dinode/inode pools; filesystem-specific reclaim such as FFS does that after generic cleanup.
- Lazy-modified special devices must be updated before reclaim loses state.
