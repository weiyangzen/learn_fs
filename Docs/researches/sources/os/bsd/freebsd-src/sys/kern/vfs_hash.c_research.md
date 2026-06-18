# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_hash.c

## Role

Provides the global VFS vnode hash table used by filesystems to locate, insert, remove, and rehash vnodes by filesystem-specific hash values. Hash buckets are salted with each mount's `mnt_hashseed`.

## Main Entry Points

- `vfs_hash_index()` computes the salted index value visible to callers.
- `vfs_hash_get()` finds and locks a matching vnode, using an optional comparison callback.
- `vfs_hash_ref()` finds a matching vnode and returns it referenced but not locked.
- `vfs_hash_insert()` inserts a newly created vnode or detects an existing matching vnode and returns that instead.
- `vfs_hash_remove()` removes a vnode from the hash list.
- `vfs_hash_rehash()` moves a vnode to a new hash bucket while the vnode is exclusively locked.
- `vfs_hash_changesize()` rebuilds the hash table when the vnode target count changes.

## Data Structures

`vfs_hash_tbl` is an array of `LIST_HEAD(vfs_hash_head, vnode)` buckets allocated with `hashinit(desiredvnodes, M_VFS_HASH, ...)`. `vfs_hash_side` temporarily holds losing insert candidates that must be `vgone()` after a duplicate is found. `vfs_hash_lock` is a global rwlock.

## Behavior

Lookup walks a salted bucket under a read lock, filters by `v_hash`, `v_mount`, and optional callback, prepares vnode acquisition with `vget_prep()`, then drops the hash lock and finishes with `vget_finish()`. If a waitable acquisition races with reclamation and returns `ENOENT`, it restarts.

Insert takes the write lock, searches for duplicates, and either inserts the new vnode into the correct bucket or abandons it by moving it to the side list, calling `vgone()` and `vput()`, and returning the existing vnode when it can be acquired.

Resize allocates a replacement table before taking the lock, swaps global table pointers under the write lock, relinks all old bucket entries using the new mask and mount salts, then frees the old table.

## Locking And Lifetime

The rwlock protects bucket membership and table replacement. Vnode lifetime during lookup is stabilized through `vget_prep()`/`vget_finish()` or `vhold()` plus `vref()` in `vfs_hash_ref()`. `vfs_hash_rehash()` requires an exclusive vnode lock, enforced by `ASSERT_VOP_ELOCKED()`.

## Dependencies

This is a low-level helper for filesystem inode-to-vnode caches. It relies on mount hash seeds initialized during mount allocation and on vnode lifecycle primitives from the broader VFS.

## Notes

The implementation prioritizes correctness under vnode reclamation races. Duplicate detection is intentionally tied to caller-provided comparison logic so filesystem-specific keys can extend beyond the integer hash.
