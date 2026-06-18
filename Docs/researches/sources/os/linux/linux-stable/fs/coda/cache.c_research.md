# File Research: sources/os/linux/linux-stable/fs/coda/cache.c

## Purpose
Implements Coda permission caching and dentry/inode invalidation helpers used after Venus downcalls or cache events.

## Main Interfaces
- Permission cache: `coda_cache_enter()`, `coda_cache_clear_inode()`, `coda_cache_clear_all()`, `coda_cache_check()`.
- Child invalidation: `coda_flag_inode_children()`.

## Control Flow
Permission cache entries are stored per inode in `coda_inode_info` as fsuid, permission mask, and global epoch. `coda_cache_enter()` records or extends permissions for the current fsuid. `coda_cache_check()` hits only when the requested mask is included, fsuid matches, and the inode epoch equals the global `permission_epoch`. `coda_cache_clear_all()` invalidates every cached permission by incrementing the global epoch.

For dentry invalidation, `coda_flag_inode_children()` finds an alias dentry for a directory inode, flags all positive child inodes with the requested Coda flag, shrinks the dcache subtree, and drops the alias.

## State And Synchronization
`permission_epoch` is atomic. Per-inode permission fields and flags are protected by `cii->c_lock`. Child dentry walking uses dentry lock plus RCU read-side protection.

## Integration Points
Used by permission checks in `dir.c`, inode revalidation, and Venus downcall handling to purge or refresh stale kernel-side Coda state.

## Risks And Review Focus
- Permission cache is fsuid-specific; changing credential semantics must preserve this.
- Child flagging intentionally does not handle negative dentries beyond dcache shrinking.
