# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/lofs/lofs_subr.c

## Role

Provides the core support routines for LOFS, illumos’s loopback filesystem. This file manages the mapping from real vnodes to LOFS shadow vnodes, plus the mapping from real VFS instances to LOFS wrapper VFS instances.

## Major Responsibilities

- Maintains a dynamically growing per-mount hash table of `lnode_t` objects.
- Creates and reuses loopback shadow vnodes through `makelonode()`.
- Creates wrapper `vfs_t` structures for real filesystems encountered under a LOFS tree.
- Handles lnode and lfsnode lifetime, reference accounting, and cleanup.
- Provides support for lock-safe hash-table growth without freeing old tables prematurely.

## Key Functions

- `lofs_subrinit()` / `lofs_subrfini()`: Create and destroy the `lnode_cache`.
- `lsetup()`: Initializes a `struct loinfo`, including the hash table, lfs list, and locks.
- `ldestroy()`: Destroys locks, current hash table, and retired hash tables at unmount time.
- `makelonode()`: Returns the LOFS vnode corresponding to a real vnode. It reuses an existing `lnode` unless `LOF_FORCE` is requested, otherwise allocates a new vnode/lnode pair, sets vnode ops, records the real vnode, and inserts into the table.
- `makelfsnode()`: Finds or creates a LOFS wrapper VFS for a real VFS. It propagates mount flags, mountpoint refstr, block size, dev/fsid, root vnode, and VFS features.
- `freelfsnode()`: Removes and destroys an idle wrapper VFS.
- `lfsfind()`: Finds an existing wrapper VFS for a real VFS, skipping stale/forced-unmounted roots.
- `lo_realvfs()`: Maps a LOFS VFS back to its real VFS and optionally returns the corresponding real root vnode.
- `lgrow()`: Resizes and rehashes the lnode table while preserving safe concurrent bucket locking.
- `lretire()`: Stores old hash tables on a retired list so concurrent stale readers never touch freed memory.
- `lsave()`: Inserts an `lnode` into its bucket and triggers growth if total refs exceed the threshold.
- `freelonode()`: Removes an lnode from the hash, releases the real vnode, frees the LOFS vnode/lnode, and reclaims idle wrapper VFS instances.
- `lfind()`: Finds and holds an existing shadow vnode for a real vnode.

## Data Structures

- `struct loinfo`: Per-mount LOFS state. Holds real/mount VFS pointers, root vnode, refcount, hash table, retired hash tables, and lfs wrapper list.
- `struct lobucket`: Hash bucket containing chain, count, and mutex.
- `lnode_t`: Maps one LOFS vnode to one real vnode.
- `struct lfsnode`: Wrapper VFS for a real VFS below the LOFS mount.
- `struct lo_retired_ht`: Retired hash table kept until unmount.

## Concurrency Model

The hash table intentionally avoids a single global lock for normal lookup. Bucket locking uses `table_lock_enter()`:

- Reads current table size and pointer.
- Locks the computed bucket.
- Verifies the table pointer and size are still current.
- Retries if a resize raced.

Growth uses `li_htlock`, then locks every old bucket and the corresponding new buckets before publishing `li_hashtable` and `li_htsize` with memory barriers. Old tables are not freed immediately; they are retired and freed only by `ldestroy()`.

The lfs wrapper list is protected separately by `li_lfslock`.

## Edge Cases and Semantics

- `LOF_FORCE` bypasses reuse and creates a distinct lnode. This is used by LOFS loop termination logic in vnode lookup.
- `makelonode()` performs non-sleeping allocation first while holding the bucket lock, then retries with sleeping allocation if needed.
- If a racing thread creates the lnode while allocation is retried, the newly allocated objects are freed and the existing lnode is used.
- Wrapper VFS reference counts intentionally stop at 1 so LOFS can free `struct lfsnode` itself rather than allowing generic VFS release to free the wrong allocation size.
- `lfsfind()` guards against real VFS pointer reuse after forced unmounts by checking the cached real root vnode.

## Dependencies

Used directly by `lofs_vfsops.c` and `lofs_vnops.c`. Depends on vnode/VFS allocation, reference counting, feature propagation, mountpoint refstr handling, atomics, mutexes, and LOFS private headers.
