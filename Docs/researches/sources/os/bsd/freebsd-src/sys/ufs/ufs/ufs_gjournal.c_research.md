# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_gjournal.c

## Purpose
Implements UFS hooks for GEOM journaling orphan tracking by maintaining unreferenced inode counters in cylinder groups and the superblock.

## Key Contents
- Internal counter updater:
  - `ufs_gjournal_modref(struct vnode *vp, int count)`
    - Determines inode cylinder group via `ino_to_cg`.
    - Resolves the real device from normal disk device or snapshot device vnode.
    - Validates inode range against filesystem inode capacity.
    - Reads cylinder group with `ffs_getcg`.
    - Updates `cg_unrefs` and `fs_unrefs` by `count`.
    - Marks superblock modified via `fs_fmod`.
    - Clears active cylinder group bit with `ACTIVECLEAR`.
    - Writes cylinder group buffer with `bdwrite`.
- Orphan hook:
  - `ufs_gjournal_orphan`
    - Returns if no gjournal provider.
    - Skips vnodes without enough references or already marked deleted.
    - Skips directories with more than `.`/`..` links and non-directories with more than one link.
    - Marks vnode `VV_DELETED`.
    - Increments unreferenced inode count.
- Close hook:
  - `ufs_gjournal_close`
    - Returns if no gjournal provider or vnode is not marked deleted.
    - If inode link count is now zero, decrements unreferenced inode count.

## Interactions
- Declared in `gjournal.h`.
- Uses `ffs_getcg`, `struct cg`, and `struct fs` from FFS.
- Updates state used for journal recovery/orphan cleanup.
