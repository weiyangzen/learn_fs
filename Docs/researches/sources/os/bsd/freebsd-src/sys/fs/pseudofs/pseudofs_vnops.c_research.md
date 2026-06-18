# File Research: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs_vnops.c

## Purpose

Implements vnode operations for pseudofs-backed synthetic filesystems. It handles visibility, lookup, attributes, open/read/write, directory enumeration, symlink reads, ioctl/extattr dispatch, reverse path lookup, and vnode reclaim.

## Main Entry Points

Visibility and lookup:
- `pfs_visible_proc()` checks process exit state, `p_cansee()`, and node visibility callbacks.
- `pfs_visible()` resolves pid to process and applies visibility.
- `pfs_lookup_proc()` obtains a held process reference for readdir.
- `pfs_lookup()` handles `.`/`..`, static child nodes, process-directory pid names, visibility, vnode-cache allocation, and namecache insertion. Delete and rename are unsupported.

Attributes and access:
- `pfs_getattr()` synthesizes file attributes, pid-adjusted file ids, timestamps, uid/gid from target process credentials, default modes, and optional consumer attr callback output.
- `pfs_access()` delegates to `vaccess()` after `VOP_GETATTR()`.
- `pfs_setattr()` silently ignores attribute changes.

Operations:
- `pfs_open()` verifies requested read/write modes against node flags and rejects advisory locks.
- `pfs_close()` calls a node close callback only on last close.
- `pfs_ioctl()` verifies a regular file, callback presence, and current visibility before invoking `pn_ioctl()`.
- `pfs_getextattr()` similarly dispatches optional extended-attribute callbacks.
- `pfs_read()` supports raw `uio` readers, buffered sbuf readers, and `PFS_AUTODRAIN` streaming reads with offset skipping.
- `pfs_write()` supports raw writers or sbuf-backed writes, capped at `PFS_MAXBUFSIZ`.
- `pfs_readdir()` lists static nodes and expands `pfstype_procdir` into visible process pid entries while holding `allproc_lock`.
- `pfs_readlink()` calls the node fill callback into a fixed path buffer.
- `pfs_vptocnp()` reconstructs vnode component names for reverse lookup and gets the parent vnode through the vnode cache.
- `pfs_reclaim()` frees vnode-cache state.

`pfs_vnodeops` registers the above plus `vfs_cache_lookup` and unsupported mutation VOPs.

## Integration Points

This file is the VFS dispatcher for all consumers registered through pseudofs, including procfs. It uses `pseudofs_internal.h` wrappers to enforce callback lock expectations and `pseudofs_vncache.c` for vnode reuse.

## Risks and Review Notes

Read paths drop the vnode lock while invoking fill callbacks and hold process references where needed. Consumer callbacks must tolerate process state changes between visibility checks and fill execution.

Directory offsets are fixed-size `PFS_DELEN` slots, not packed `dirent` sizes. Readers must use valid aligned offsets and buffer sizes.
