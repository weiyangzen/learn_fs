# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clsubs.c

## Summary
Small NFS client support module for initialization, attribute-cache lookup, directory-cookie tracking, vnode exclusive-access helpers, and write-verifier cleanup.

## Main Responsibilities
- Initializes async I/O daemon state and the NFS node hash table.
- Rejects client unload, matching the unsupported unload policy in the module layer.
- Provides directory cookie-map locking and cookie lookup/allocation.
- Provides an extra per-node exclusive lock helper for shared-vnode-lock callers.
- Serves cached attributes when valid and synchronizes vnode pager size on cache hits.
- Invalidates directory cookie state after directory changes.
- Clears `B_NEEDCOMMIT` dirty buffers when the server write verifier changes.

## Key APIs
- `ncl_init()`, `ncl_uninit()`.
- `ncl_dircookie_lock()`, `ncl_dircookie_unlock()`, `ncl_getcookie()`, `ncl_invaldir()`.
- `ncl_excl_start()`, `ncl_excl_finish()`.
- `ncl_getattrcache()`.
- `ncl_clearcommit()`.

## Important Behavior
`ncl_getattrcache()` computes adaptive attribute-cache timeout from mount `acregmin/acregmax/acdirmin/acdirmax` values and file modification age. It treats valid delegations as allowing cached attrs, counts cache hits/misses, reconciles cached regular-file size with local dirty state, may call `ncl_pager_setsize()`, overlays local atime/mtime changes, and fires DTrace cache hit/miss probes.

`ncl_getcookie()` maps logical directory offsets to NFS cookies in chained `nfsdmap` blocks. It refuses offsets above 50 GiB to avoid truncating the calculated cookie index and can allocate cookie-map blocks when `add` is set.

`ncl_clearcommit()` walks all vnodes on a mount and clears `B_NEEDCOMMIT` and `B_CLUSTEROK` on dirty buffers that need recommit after a write verifier change.

## State and Synchronization
Uses `ncl_iod_mutex` for async daemon state, per-node `n_mtx` plus `NDIRCOOKIELK` for directory cookie maps, per-node `n_excl` for exclusive operation serialization, vnode/bufobj locks for dirty-buffer scanning, and global `nfsstatsv1` counters.

## Risks
Attribute-cache validity depends on delegation status, mount timeout tuning, local dirty-size handling, and correct pager-size updates outside node locks. Directory cookie maps assume stable offset-to-cookie mapping until invalidated. `ncl_clearcommit()` walks all mount vnodes and mutates dirty-buffer flags only when buffers are not locked, so verifier recovery depends on later writeback behavior for buffers it cannot touch.
