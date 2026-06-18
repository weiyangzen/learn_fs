# File Research: sources/os/bsd/netbsd-src/sys/fs/hfs/hfs_vfsops.c

## Purpose
Implements NetBSD VFS operations for the HFS/HFS+ filesystem: module attach, mount, unmount, root lookup, statvfs, vnode caching/loading, and lifecycle initialization.

## Main Entry Points
- `MODULE()` and `hfs_modcmd()` attach/detach the VFS module.
- `hfs_vfsops` declares the mount, unmount, root, statvfs, sync, vget, loadvnode, file-handle, init, and done hooks.
- `hfs_mount()` handles mount arguments, device lookup, permission authorization, and calls `hfs_mountfs()`.
- `hfs_mountfs()` allocates `hfsmount`, initializes callback arguments, opens the volume through `hfslib_open_volume()`, rejects dirty journaled volumes, and sets mount block shifts.
- `hfs_unmount()` flushes vnodes, closes the libhfs volume, releases the device vnode, and frees mount state.
- `hfs_root()` resolves `HFS_CNID_ROOT_FOLDER`.
- `hfs_statvfs()` reports allocation-block size, block totals, free blocks, and file counts from the HFS+ volume header.
- `hfs_vget()` and `hfs_vget_internal()` resolve CNID plus fork into vcache keys.
- `hfs_loadvnode()` allocates an `hfsnode`, reads the catalog record by CNID, initializes vnode/genfs state, stores parent CNID, selects data/resource fork size, and returns the stable cache key.
- `hfs_init()` creates pools, attaches malloc type, registers libhfs callbacks, and initializes libhfs global state.
- `hfs_done()` tears down malloc/pool/libhfs state.

## Dependencies
Uses NetBSD VFS, vnode cache, module framework, genfs, specfs, pool allocator, kauth mount authorization, and `libhfs` callbacks.

## Risks and Notes
Live remount/update support is disabled. File handles are unsupported: both `hfs_fhtovp()` and `hfs_vptofh()` return `EOPNOTSUPP`. `hfs_mountfs()` frees `hfsmount` on failure but does not itself clear `mp->mnt_data` in the shown error path. Journaled volumes mount only if the journal appears clean; there is no replay. The filesystem is effectively read-only at the vnode layer.
