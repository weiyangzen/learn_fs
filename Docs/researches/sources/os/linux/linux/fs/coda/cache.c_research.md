# File Research: sources/os/linux/linux/fs/coda/cache.c

Coda kernel minicache helpers for permission caching and dentry/inode invalidation.

Key behavior:
- Maintains a global `permission_epoch` atomic counter.
- `coda_cache_enter()` caches permission mask for current fsuid on an inode; same uid extends mask, different uid replaces mask.
- `coda_cache_clear_inode()` invalidates one inode’s cached permissions by setting stale epoch.
- `coda_cache_clear_all()` invalidates all inode permission caches by incrementing global epoch.
- `coda_cache_check()` validates requested mask, current fsuid, and epoch.
- `coda_flag_inode_children()` finds an alias dentry for a directory, flags child inodes, shrinks child dcache, and drops alias.

Concurrency:
- Per-inode `c_lock` protects cached permission fields.
- Child dentry traversal uses parent d_lock plus RCU read lock.
- Permission cache is intentionally simple: one uid/mask/epoch slot per inode.

Integration:
- Used by Coda permission checks and Venus downcall invalidation paths.
- Flags such as `C_PURGE`, `C_FLUSH`, and `C_VATTR` are consumed by dentry revalidation and inode revalidation.
