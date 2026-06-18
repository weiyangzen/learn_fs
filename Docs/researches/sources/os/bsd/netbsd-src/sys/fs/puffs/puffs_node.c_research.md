# File Research: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_node.c

This file manages PUFFS vnode/node allocation, vnode cache lookup, node references, root vnode construction, and local metadata cache updates. It defines the global pools `puffs_pnpool` and `puffs_vapool`, initialized in `puffs_vfsops.c`.

`puffs_getvnode1()` is the main vnode acquisition routine. It validates server-provided vnode type and size, obtains or creates a vnode through `vcache_get()` keyed by the userspace cookie, waits until `puffs_vfsop_loadvnode()` has initialized `v_data`, rejects existing vnodes when a fresh node is required, and finalizes new vnodes by setting `v_type`, special/fifo operation vectors, spec device state, and regular-file UVM size. `puffs_getvnode()` allows existing nodes; `puffs_newnode()` requires a new cookie, rejects root-cookie reuse, calls `puffs_getvnode1(..., may_exist=false)`, enters the namecache if enabled, and updates parent metadata.

`puffs_putvnode()` tears down genfs state, clears `v_data` under `v_interlock` to interlock with `puffs_getvnode1()`, and releases the puffs-node reference. `puffs_makeroot()` ensures the root vnode exists and stores it in `pmp_root`. `puffs_cookie2vnode()` maps a userspace cookie back to an in-kernel vnode, with special handling for root and a `PUFFS_NOSUCHCOOKIE` result for stale cache-created `VNON` nodes.

`puffs_updatenode()` records local metacache updates for atime, ctime, mtime, and size, setting `PNODE_METACACHE_*` flags. `puffs_referencenode()` and `puffs_releasenode()` maintain `pn_refcount` independent of vnode references to avoid vnode inactive/deadlock paths during async operations; final release destroys mutexes/select state, returns cached vattrs, and frees the node pool entry.
