# File Research: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs_vncache.c

## Purpose

Implements the shared pseudofs vnode cache, keyed by pseudofs node, pid, and mount.

## Main Entry Points

`pfs_vncache_load()` initializes the global cache mutex, hash table, and process-exit event handler.

`pfs_vncache_unload()` deregisters the process-exit handler, purges all cached vnodes, asserts the cache is empty, destroys the mutex, and destroys the hash table.

`pfs_vncache_alloc()`:
- checks for an existing vnode for `(mount, pfs_node, pid)`.
- uses `vget_prep()`/`vget_finish()` to safely acquire cached vnodes.
- purges namecache entries on hits to avoid duplicate VFS cache entries by later callers.
- allocates a new vnode and `pfs_vdata` on misses.
- maps pseudofs node type to vnode type and root/procdep vnode flags.
- inserts the vnode into the mount queue and then into the cache.
- handles races by rechecking the cache after vnode construction and discarding the loser vnode.

`pfs_vncache_free()` removes vnode private data from the cache and frees it during reclaim.

`pfs_purge()` and `pfs_purge_all()` revoke cached vnodes, restarting scans because `vgone()` can sleep and mutate the cache.

`pfs_exit()` purges process-dependent vnodes for an exiting pid.

## Integration Points

Used by `pfs_root()`, pseudofs lookup, `vptocnp`, reclaim, node destroy, module load/unload, and process-exit cleanup.

## Risks and Review Notes

The purge path intentionally restarts scans after each `vgone()` to avoid holding the cache mutex across sleeping vnode teardown. This is safe but potentially expensive for large caches.
