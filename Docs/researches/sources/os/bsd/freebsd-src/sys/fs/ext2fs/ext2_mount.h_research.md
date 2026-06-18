# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_mount.h

## Purpose
Defines the FreeBSD in-kernel ext2 mount-private structure and mount helper macros.

## Main Elements
- `struct ext2mount` stores the VFS mount, device cdev/vnode, in-memory ext2 superblock, indirect-block geometry, mount mutex, GEOM consumer, and backing `bufobj`.
- Declares `M_EXT2NODE` for inode-private allocation.
- Defines `EXT2_LOCK`, `EXT2_UNLOCK`, and `EXT2_MTX`.
- Defines `VFSTOEXT2(mp)` for retrieving ext2 mount data.
- Provides mapping helpers used by bmap/allocation paths: `MNINDIR`, `blkptrtodb`, and `is_sequential`.

## Dependencies And Integration
Included by ext2 VFS, vnode, bmap, allocation, lookup, and inode code. The `um_lock` mutex protects shared mount and filesystem accounting state.

## Risk Notes
Incorrect geometry fields (`um_nindir`, `um_bptrtodb`, `um_seqinc`) would affect logical-to-physical mapping and sequential allocation heuristics across the filesystem.
