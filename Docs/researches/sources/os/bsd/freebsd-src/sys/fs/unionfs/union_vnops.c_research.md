# File Research: sources/os/bsd/freebsd-src/sys/fs/unionfs/union_vnops.c

## Summary
Implements the FreeBSD unionfs vnode operation vector. It routes VOPs to an upper or lower vnode, creates upper-layer shadow objects on demand, handles whiteouts, manages copy-up for writes and metadata mutations, and supplies unionfs-specific locking/reclaim behavior.

## Main Responsibilities
- Implements lookup, create, remove, rename, mkdir/rmdir, symlink, link, open/close, read/write, readdir, ACL, extattr, MAC label, vnode locking, strategy, writecount, text, and UNIX-domain socket VOPs.
- Presents upper-layer contents when present, otherwise falls back to lower-layer contents.
- Performs copy-up for lower regular files before write-like operations, locks, ACL/label/extattr mutation, and some rename/link paths.
- Creates shadow directories in the upper layer when traversing or renaming lower-only directories.
- Creates whiteouts when deleting or renaming over lower-layer entries, depending on mount whiteout mode and lower vnode presence.

## Key APIs and Operations
- `unionfs_lookup()` is the central name resolution path. It looks up lower first, then upper, handles dot/dotdot, whiteout and opaque directory behavior, shadow directory creation, unionfs vnode creation, cache insertion, and serialized in-progress directory lookups.
- `unionfs_open()` and `unionfs_close()` track per-thread node status and lower/upper open counts, copy lower regular files before write opens, open lower directories for merged readdir, and keep `vp->v_object` aligned with the active backing vnode.
- `unionfs_readdir()` reads upper entries first, then lower entries unless the upper directory is opaque. It tracks readdir state in `unionfs_node_status` and merges cookies when both layers are read.
- `unionfs_rename()` maps unionfs source/target vnodes to upper backing vnodes, copy-ups lower-only sources, creates shadow dirs or copies symlinks/files, rejects unsupported flags and cross-device operations, and returns `ERELOOKUP` when dropped locks require lookup replay.
- `unionfs_lock()` locks the active backing vnode rather than the unionfs vnode itself, restarting if a lower lock becomes invalid due to concurrent copy-up or reclaim.
- `unionfs_vnodeops` registers the operation vector with `VFS_VOP_VECTOR_REGISTER()`.

## Important Behavior
Writes target the upper vnode once one exists. If a write-like operation targets a lower regular file, unionfs generally calls `unionfs_copyfile()` first, then uses the new upper vnode.

Directory behavior is layered. Lookups may synthesize a unionfs vnode from both upper and lower vnodes, may suppress lower entries under whiteouts or opaque upper directories, and may create an upper shadow directory for lower directories when the mount is writable.

Delete operations act on upper vnodes when present and create whiteouts when lower entries must be hidden. Lower-only deletes create a whiteout instead of modifying the lower filesystem.

Several helper paths deliberately exchange locks instead of holding upper and lower vnode locks together. `unionfs_lock_lvp()` and `unionfs_unlock_lvp()` drop the unionfs/default lock while operating on a lower vnode to reduce cross-filesystem lock-order problems.

## State and Lifetime
Per-vnode state lives in `struct unionfs_node`, reached through `VTOUNIONFS()`. Per-thread open/readdir state lives in `struct unionfs_node_status`. Reclaim removes unionfs node state with `unionfs_noderem()`, inactive clears `v_object` and recycles the vnode.

The code relies on vnode references, holds, `VI_LOCK`, and backing vnode locks to survive lock drops during copy-up, lower locking, rename replay, and unmount/reclaim races.

## Risks
This file is lock-order sensitive. Many paths intentionally drop and reacquire vnode locks, return `ERELOOKUP`, or restart lock acquisition to avoid stale upper/lower backing choices. Copy-up and whiteout behavior is also security-sensitive because it changes whether later VOPs affect upper storage, lower storage, or only name visibility.
