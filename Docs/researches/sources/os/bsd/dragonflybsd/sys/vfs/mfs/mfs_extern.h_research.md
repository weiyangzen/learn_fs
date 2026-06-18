# File Research: sources/os/bsd/dragonflybsd/sys/vfs/mfs/mfs_extern.h

## Scope

Declares external interfaces for the memory filesystem implementation.

## APIs

- Forward declares `struct buf`, `struct mfsnode`, `struct mount`, `struct thread`, and `struct vnode`.
- Declares `mfs_getimage()`, `mfs_mountfs()`, and `mfs_mountroot()`.

## Dependencies

Used by MFS implementation code and related UFS/FFS integration points that need MFS entry points without pulling in full definitions.

## Risks And Invariants

This header is small and mostly historical; the implemented file in this group provides `mfs_mount`/`mfs_start` VFS hooks rather than all declared legacy-style names directly.
