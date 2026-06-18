# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sharefs/sharefs_vfsops.c

## Purpose

`sharefs_vfsops.c` implements the VFS/module side of the kernel `sharefs` pseudo filesystem. `sharefs` exposes the in-kernel share table as a read-only pseudo-file, traditionally mounted as `sharetab`.

## Main Interfaces

The file defines module entry points `_init`, `_info`, and `_fini`, registers the `sharefs` filesystem and `sharefs` syscall, initializes vnode and VFS operation vectors, and exports `sharefs_ops_data`.

The VFS operation table `sharefs_vfstops[]` installs `sharefs_mount`, `sharefs_unmount`, `sharefs_root`, and `sharefs_statvfs`.

## Behavior And Data Flow

`sharefs_init()` records the filesystem type, installs VFS ops with `vfs_setfsops()`, creates GFS vnode operation vectors with `gfs_make_opsvec()`, allocates a pseudo-device major, and initializes per-zone sharetab state through `sharefs_sharetab_init()`.

`sharefs_mount()` requires mount privilege, rejects non-overlay busy mountpoints, allocates `sharefs_vfs_t`, assigns a unique pseudo-device/minor pair, fills `vfs_bsize`, `vfs_fstype`, `vfs_fsid`, `vfs_data`, and `vfs_dev`, then creates the root pseudo-file via `sharefs_create_root_file()`.

`sharefs_unmount()` requires unmount privilege, rejects forced unmounts, checks that no active vnodes hold the root beyond the mount reference, releases the root vnode, and frees the per-mount data. `sharefs_root()` returns the root vnode with a hold. `sharefs_statvfs()` returns a one-file, read-only pseudo-filesystem view.

## Dependencies

This file depends on GFS pseudo-file helpers, `sharefs/sharefs.h`, VFS registration, module/syscall registration, mount policy checks, pseudo-device allocation, and `sharefs_vnops.c` for root-file construction.

## Research Notes

The filesystem is intentionally non-unloadable: `_fini()` always returns `EBUSY`. The notable correctness points are per-mount pseudo-device uniqueness, root vnode reference accounting during unmount, and the relationship between VFS initialization and per-zone sharetab initialization.
