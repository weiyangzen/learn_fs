# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_hash.c

Source read: complete file, 172 lines.

Purpose: In-core HPFS node hash table keyed by device and fnode sector number. It prevents duplicate vnodes for the same on-disk fnode and supports lookup/vget during VFS operations.

Key interfaces:
- `hpfs_hphashinit()` initializes a lock, allocates the hash table with `hashinit()`, and initializes the LWKT token.
- `hpfs_hphash_uninit()` destroys the hash table during VFS uninit.
- `hpfs_hphashlookup()` returns a matching `hpfsnode` without taking a vnode reference.
- `hpfs_hphashvget()` finds and exclusively vgets a vnode, then revalidates the hash entry after possible blocking.
- `hpfs_hphashins()` marks a node hashed and inserts it.
- `hpfs_hphashrem()` removes a hashed node and clears diagnostic links under `DIAGNOSTIC`.

Integration:
- Used by `hpfs_vget()` and `hpfs_reclaim()` in `hpfs_vfsops.c`/`hpfs_vnops.c`.
- Protected by `hpfs_hphash_token`; node creation is also serialized with `hpfs_hphash_lock`.

Risks and review notes:
- `hpfs_hphash_uninit()` destroys the table without explicitly nulling `hpfs_hphashtbl`.
- Correctness depends on the revalidation loop in `hpfs_hphashvget()` because `vget()` can block and race with reclaim.
