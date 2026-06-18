# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clnode.c

`nfs_clnode.c` implements NFS client node/vnode allocation, lookup, inactive/reclaim cleanup, sillyrename cleanup, and cache invalidation.

Key functions and behavior:
- `ncl_nhinit()` creates the UMA zone for `struct nfsnode`.
- `ncl_nhuninit()` destroys the node UMA zone.
- `ncl_nget()` looks up or creates an NFS vnode/nfsnode by file handle. It hashes the file handle, searches the mount vnode hash, allocates a new node/vnode on miss, initializes mutex and exclusive lock, enables recursive/shared vnode locking, marks root vnodes, attaches the file handle, inserts into mount queue and vnode hash, and handles racing insert losers.
- `nfs_freesillyrename()` asynchronously releases the saved directory vnode and frees sillyrename state.
- `ncl_releasesillyrename()` detaches sillyrename state from non-directory vnodes, optionally invalidates buffers, removes the silly-renamed file, frees credentials, and queues directory vnode release to avoid lock-order reversal.
- `ncl_inactive()` handles last-use vnode processing. For NFSv4 regular files it clears the current open stateid, flushes dirty pages/buffers as needed before delayed close, performs `nfsrpc_close()`, releases sillyrename state, and retains only meaningful post-inactive flags (`NMODIFIED`, `NDSCOMMIT`).
- `ncl_reclaim()` performs final vnode teardown: lets NLM abort pending locks, releases sillyrename, closes remaining NFSv4 opens, returns delegations before hash removal when not unmounting, removes from vnode hash, saves delegation attributes via `nfscl_reclaimnode()`, frees directory cookie maps, write credentials, file handle, v4 node data, mutex/lock, and UMA node storage.
- `ncl_invalcaches()` invalidates all access-cache entries and the attribute cache for a vnode, firing DTrace flush probes.

Important integration points:
- Uses FreeBSD vnode hash and mount queue APIs to provide one vnode per file handle per mount.
- Coordinates with NFSv4 state management (`nfsrpc_close`, delegation return, open stateid clearing), VM/page flushing, buffer invalidation, NLM lock reclaim hook, and DTrace cache probes.
- Sillyrename cleanup is split into a taskqueue release to avoid vnode lock-order reversal when dropping the directory vnode reference.

Research notes:
- This is the client vnode lifecycle file. Correct ordering matters because vnode reclaim can race with close, delegation recall, unmount, delayed writes, NLM locks, and sillyrename cleanup.
