# File Research: sources/os/linux/linux/fs/9p/vfs_dentry.c

Implements 9p dentry lifecycle and cached dentry revalidation.

Key behavior:
- `v9fs_cached_dentry_delete()` prevents caching of negative dentries.
- `v9fs_dentry_release()` detaches and drops all FIDs stored on a dentry.
- `__v9fs_lookup_revalidate()`:
  - Rejects RCU lookup.
  - Treats negative dentries as valid.
  - If inode attributes are invalid, looks up a FID and refreshes inode attributes through legacy or dotl refresh.
  - Invalidates the dentry on `-ENOENT` or type-change persistence.
- Provides dentry unalias lock/unlock callbacks using the session `rename_sem`.
- Defines cached dentry operations with revalidate/delete/release/unalias hooks.
- Defines uncached dentry operations with release/unalias hooks only.

Important interactions:
- Cached modes in `vfs_super.c` select `v9fs_cached_dentry_operations`; uncached modes select `v9fs_dentry_operations` and `DCACHE_DONTCACHE`.
- Dentry release is also called after successful remove to invalidate dentry-held FIDs.
