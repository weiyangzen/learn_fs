# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_vnops.c

Source read: complete file, 1184 lines.

Purpose: HPFS vnode operation implementation. It supports ioctl access to inline extended attributes, bmap/read/write, getattr/setattr, inactive/reclaim, strategy, access checks, readdir, lookup, create/remove stubs, fsync, pathconf, and the vnode op table.

Key interfaces:
- `hpfs_ioctl()` implements EA count, EA size, and EA read ioctls by walking inline `fn_int` EA records.
- `hpfs_bmap()` maps logical byte offsets to device offsets through `hpfs_hpbmap()`.
- `hpfs_read()` maps runs, reads from the device vnode, and `uiomove()`s data out.
- `hpfs_write()` supports append, extends allocation as needed, writes full or partial blocks, and uses sync or async writeback based on `IO_SYNC`.
- `hpfs_getattr()` returns vnode attributes from `hpfsnode`/fnode state and validates parent dirent metadata when needed.
- `hpfs_setattr()` rejects mode/uid/gid/flags changes, supports time updates, and grows/shrinks regular files through `hpfs_extend()`/`hpfs_truncate()`.
- `hpfs_fsync()` flushes dirty buffers with `vfsync()` and writes fnode metadata through `hpfs_update()`.
- `hpfs_inactive()` writes changed fnode or parent-dir metadata and recycles invalid nodes.
- `hpfs_reclaim()` removes hash entries, releases the device vnode, detaches `v_data`, and frees the node.
- `hpfs_readdir()` fakes `.` and `..`, walks HPFS directory down-pointer trees, converts names through `hpfs_d2u()`, and optionally emits NFS cookies.
- `hpfs_lookup()` handles `.`, `..`, access checks, directory searches, VFS_VGET, parent locking flags, and create/delete lookup semantics.
- `hpfs_strategy()` resolves unmapped bios through VOP_BMAP and forwards to the device vnode.
- `hpfs_pathconf()` reports HPFS link/name/path and chown/truncation constraints.

Integration:
- `hpfs_vnode_vops` wires these routines into DragonFly VOP dispatch.
- Uses helpers from `hpfs_subr.c`, `hpfs_alsubr.c`, and `hpfs_lookup.c`.

Risks and review notes:
- Write-side directory operations route to helpers that return `EOPNOTSUPP`, so create/remove VOP entries exist but are not functional.
- `hpfs_ioctl()` prints EA names with `%s` while EA names are length-delimited in the on-disk format; malformed or unterminated names could overrun debug output expectations.
- `hpfs_read()` and `hpfs_write()` compute `resid`/transfer sizes with unsigned and signed conversions; boundary behavior near EOF and large offsets should be tested.
- Readdir's tree walk uses a synthetic numeric offset rather than stable byte offsets; this is simple but can be fragile for NFS-style cookie expectations if directories changed, though HPFS mutation is largely unsupported.
