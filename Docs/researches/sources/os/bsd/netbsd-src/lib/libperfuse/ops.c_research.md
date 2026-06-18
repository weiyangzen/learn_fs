# File Research: sources/os/bsd/netbsd-src/lib/libperfuse/ops.c

## Purpose
Implements the PUFFS vnode/filesystem operation layer for `libperfuse`, translating NetBSD PUFFS callbacks into FUSE protocol requests and replies.

## Main Responsibilities
- Filesystem operations: init, unmount, statvfs, sync, pathconf, suspend, unimplemented fh conversions.
- Node operations: lookup, create, mknod, open/close, access, getattr/setattr, poll, fsync, remove/link/rename, mkdir/rmdir/symlink, readdir, readlink, reclaim/inactive, read/write, advlock, extattr, fallocate.
- Converts FUSE attributes and directory entries to NetBSD `vattr` and `dirent`.
- Tracks FUSE node ids, lookup counts, file handles, dirty state, removed/reclaimed state, and per-node request queues.
- Serializes sensitive operations with `requeue_request` / `dequeue_requests`: open, resize/getattr/setattr/write size updates, readdir buffering, after-write, after-FUSE-exchange, and reclaim references.

## Key Implementation Notes
- `xchg_msg()` is the central FUSE exchange wrapper. It increments global/per-node in-flight counters, optionally traces calls, destroys failed messages, and wakes operations waiting for `PCQ_AFTERXCHG`.
- `node_lookup_common()` sends `FUSE_LOOKUP`, reuses cached nodes by FUSE nodeid, handles ABI 7.4 negative lookup `ino == 0`, fills PUFFS newinfo, and increments FUSE/PUFFS lookup counters.
- `perfuse_node_create()` prefers `FUSE_CREATE`, caches `ENOSYS` as `PS_NO_CREAT`, then falls back to `mknod + open`.
- `perfuse_node_access()` normally uses local `puffs_access` emulation because `PS_NO_ACCESS` is set by default elsewhere; it can probe `FUSE_ACCESS` when enabled.
- `perfuse_node_setattr_ttl()` has detailed permission checks and special handling for resize plus chmod on open handles to avoid remote filesystem ordering failures.
- `perfuse_node_readdir()` reads all FUSE directory entries into a FUSE buffer, converts to native `dirent`, buffers output on the node, and serializes concurrent readdir on a node.
- `perfuse_node_reclaim2()` manages FUSE `FORGET`, lookup counters, cache removal, queued-operation drainage, and final `perfuse_destroy_pn`.
- Read/write split large transfers by `ps_max_readahead` / `ps_max_write`; write updates cached size, dirty flags, and sync statistics.
- Extended attributes map NetBSD user/system namespaces to Linux/FUSE xattr names via helpers in `subr.c`.

## Dependencies
- Internal: `perfuse_priv.h`, `fuse.h`, node/cache/file-handle helpers from `subr.c`, callbacks registered in `perfuse.c`.
- External: PUFFS, FUSE protocol structs, NetBSD vnode-style access helpers and extattr definitions.
