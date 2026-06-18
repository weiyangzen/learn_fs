# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_vfs.c

## Purpose
Implements objfs module linkage, filesystem initialization, and VFS operations for the kernel object filesystem.

## Main Entry Points
- `_init()`, `_info()`, and `_fini()` provide module linkage; `_fini()` returns `EBUSY` because objfs cannot be unloaded.
- `objfs_init()` registers VFS ops, builds GFS vnode op vectors, obtains a unique device major, and initializes data-file section metadata.
- `objfs_mount()` validates permission/mountpoint state, assigns a unique device/fsid, allocates `objfs_vfs_t`, and creates the root vnode.
- `objfs_unmount()` rejects forced unmounts, checks for active vnodes, releases the root vnode, and frees vfs-private data.
- `objfs_root()` returns the held root vnode.
- `objfs_statvfs()` reports pseudo-filesystem stats.

## Internal Mechanics
Objfs is declared as `"objfs"` with `VSW_HASPROTO | VSW_ZMOUNT`. It has three GFS operation vectors: root directory, object directory, and data file. Mount allocates a synthetic device number using `objfs_major` and atomically incremented `objfs_minor`, avoiding already mounted device ids.

Unmount expects only the caller and root vnode references to remain. Active object/data vnodes hold the root, so a root vnode count above one yields `EBUSY`.

## Dependencies
Uses illumos module linkage, VFS registration APIs, GFS op-vector construction, mount policy checks, unique device allocation, objfs node constructors, and common objfs object counting.

## Risks and Notes
- Forced unmount is explicitly unsupported.
- Objfs is non-unloadable, likely because exported module-object views and global initialized data are intended to persist.
- Stat values are pseudo values based on loaded object count rather than storage capacity.
