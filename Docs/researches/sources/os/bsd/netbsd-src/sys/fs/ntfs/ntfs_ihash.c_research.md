# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_ihash.c

Implements the in-core NTFS ntnode hash table.

Key points:
- Maintains a hash table keyed by device and inode number.
- `ntfs_nthashinit()` initializes global hash locks and table.
- `ntfs_nthashreinit()` rebuilds the hash table when vnode sizing changes.
- `ntfs_nthashdone()` frees table and destroys locks.
- `ntfs_nthashlookup()` returns a matching in-core `ntnode` without taking its per-node busy lock.
- `ntfs_nthashins()` inserts an ntnode and marks `IN_HASHED`.
- `ntfs_nthashrem()` removes an ntnode if currently hashed.

Interactions:
- Used by `ntfs_ntlookup()` / `ntfs_ntput()` in `ntfs_subr.c`.
- Coordinates with global `ntfs_hashlock` and local hash-table lock.

Risk/notes:
- Hash lookup itself does not acquire object lifetime ownership; callers handle locking/refcounting.
