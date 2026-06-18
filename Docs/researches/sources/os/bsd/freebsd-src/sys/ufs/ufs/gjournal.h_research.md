# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/gjournal.h

## Purpose
Declares the UFS hooks used by GEOM journaling support.

## Key Contents
- `ufs_gjournal_orphan(struct vnode *fvp)`
- `ufs_gjournal_close(struct vnode *vp)`

## Interactions
- Implemented in `ufs_gjournal.c`.
- Updates UFS unreferenced inode counters when gjournal tracks orphaned/deleted vnodes.
