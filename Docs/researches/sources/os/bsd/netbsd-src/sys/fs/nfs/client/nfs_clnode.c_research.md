# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clnode.c

This file implements core nfsnode allocation, root-node lookup, vnode inactive/reclaim handling, sillyrename cleanup, and cache invalidation.

Key entry points:
- `ncl_nhinit()` creates the `NCLNODE` UMA zone for `struct nfsnode`.
- `ncl_nhuninit()` destroys that zone.
- `ncl_nget()` looks up or creates an nfsnode by file handle; this variant is documented as root-directory oriented.
- `ncl_inactive()` handles vnode inactivity, including delayed NFSv4 close for regular files after mmap/page-cache flush.
- `ncl_reclaim()` tears down an nfsnode and vnode association.
- `ncl_invalcaches()` clears both access-cache entries and the attribute cache.

Important behavior:
- `ncl_nget()` hashes file handles with FNV, searches `vfs_hash`, allocates a new vnode/nfsnode on miss, attaches buffer ops, initializes `n_mtx`, sets recursive/shared vnode locking flags, marks the root vnode when the file handle matches the mount root, and inserts into the mount queue/hash.
- Sillyrename cleanup is split: `ncl_releasesillyrename()` invalidates buffers, removes the silly-renamed file, drops credentials, and defers directory `vrele()` through `sysmon_task_queue_sched()` to avoid lock-order reversal.
- `ncl_inactive()` flushes VM pages and NFS buffers before issuing delayed NFSv4 close, then preserves only `NMODIFIED` among nfsnode flags.
- `ncl_reclaim()` gives NLM a chance to abort locks, releases sillyrename state, destroys VM objects, closes remaining NFSv4 opens, removes the vnode from `vfs_hash`, calls `nfscl_reclaimnode()` for regular files, frees directory cookie maps, credentials, file handles, NFSv4 name state, mutexes, and the UMA allocation.

Dependencies:
- Uses `newnfs_vnodeops`, `buf_ops_newnfs`, `newnfs_vncmpf()`, `ncl_vinvalbuf()`, `ncl_flush()`, `nfsrpc_close()`, `nfscl_reclaimnode()`, and optional `nfs_reclaim_p`.
- Uses DTrace cache flush macros when invalidating caches.

Research notes:
- This is the lifecycle companion to the I/O files: it owns node identity and teardown, while `nfs_clbio.c` owns cached data movement.
- NFSv4 delayed close semantics make inactive/reclaim more than simple memory cleanup.
