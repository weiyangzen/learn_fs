# File Research: sources/os/bsd/freebsd-src/sys/fs/nullfs/null_vnops.c

This file implements nullfs vnode operations and the generic stackable VOP bypass layer.

Core design:
- `null_bypass()` rewrites nullfs vnode arguments to their lower vnodes, calls the lower vnode operation, restores original upper vnode arguments, and wraps returned lower vnodes with `null_nodeget()`.
- The bypass path tracks operations that release vnode references and compensates with temporary references.
- Temporary holds protect lower/upper vnode relationships across lower VOPs that may unlock and allow reclamation.
- `null_copy_inotify()` synchronizes inotify routing flags between upper and lower vnodes.

Specialized VOP behavior:
- `null_lookup()` directly calls lower `VOP_LOOKUP()` for speed, rejects read-only creates/deletes/renames, handles `..` edge cases, holds the lower directory vnode across unlock/reclaim races, and wraps lower results.
- `null_open()` forwards open and then shares the lower vnode VM object/page-read state.
- `null_setattr()`, `null_access()`, and `null_accessx()` enforce read-only mount semantics before bypass.
- `null_stat()` and `null_getattr()` forward then rewrite fsid to the upper mount fsid.
- `null_remove()` and `null_rmdir()` mark the vnode for drop; remove also temporarily references the lower vnode to support lower NFS sillyrename behavior.
- `null_rename()` prevents cross-device/null-to-lower moves, maps all participating vnodes manually, and marks overwritten targets for drop.
- `null_lock()` and `null_unlock()` mostly lock/unlock the lower vnode, with SMR/interlock preparation and fallback to standard locking if the null node has been reclaimed.
- `null_inactive()` recycles the vnode when caching is disabled, the lower vnode was deleted, or the lower vnode is `VV_NOSYNC`.
- `null_reclaim()` removes the hash entry, detaches `v_data`, restores private vnode lock, clears VM object and inotify flags, unwinds writecounts, releases the lower vnode, and frees the null node.
- `null_vptocnp()`, `null_vptofh()`, `null_read_pgcache()`, `null_advlock()`, `null_vput_pair()`, and `null_getlowvnode()` provide targeted lower-vnode forwarding where generic bypass is unsafe.

VOP vectors:
- `null_vnodeops` defines the main operation table.
- `null_vnodeops_no_unp_bypass` inherits from `null_vnodeops` but uses standard UNIX-domain socket bind/connect/detach operations.

Research-relevant risks:
- Lock ownership can move between lower and upper vnodes during reclaim; several routines explicitly repair this state.
- Generic bypass assumes at most one returned vnode pointer and no inout vnode pointers.
- Reclaim must prevent upper inotify callbacks after lower vnode watch references outlive the upper vnode.
- `copy_file_range` is deliberately `VOP_PANIC`, so generic bypass is not used there.
