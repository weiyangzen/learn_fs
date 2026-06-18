# File Research: sources/os/linux/linux/fs/orangefs/dcache.c

Implements OrangeFS dentry revalidation.

Key behavior:
- `orangefs_revalidate_lookup()` sends an `ORANGEFS_VFS_OP_LOOKUP` upcall for the parent/name pair.
- Positive dentries are kept only if lookup succeeds and the returned handle matches the cached inode.
- Negative dentries are kept only if lookup still returns `-ENOENT`.
- Successful revalidation refreshes `d_fsdata` timeout via `orangefs_set_timeout()`.
- `orangefs_d_revalidate()` trusts unexpired dentries, rejects RCU lookup with `-ECHILD`, always trusts root, and then validates positive inode contents with `orangefs_inode_check_changed()`.

Important invariants:
- Dentry timeout is jiffies-based and configured by `orangefs_dcache_timeout_msecs`.
- Lookup and getattr revalidation are distinct: name validity is checked first, inode attribute freshness second.
