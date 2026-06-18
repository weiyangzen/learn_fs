# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_mount.h

This header defines DragonFlyBSD ext2 mount arguments, the in-memory ext2 mount wrapper, locking macros, mount conversion macros, and geometry helpers used by mapping/allocation code.

Key responsibilities:
- Declare `struct ext2_args` for mount input.
- Declare `struct ext2mount`, which ties VFS mount state to device vnode, ext2 superblock state, buffer object, geom consumer, lock, and export data.
- Provide mount lock/unlock/assert access macros.
- Convert `struct mount` to `struct ext2mount`.
- Provide indirect-block geometry helpers for bmap.

Important definitions:
- `struct ext2_args`: Device path and export arguments.
- `struct ext2mount`: `um_mountp`, `um_dev`, `um_devvp`, `um_e2fs`, `um_nindir`, `um_bptrtodb`, `um_seqinc`, `um_lock`, `um_cp`, `um_bo`, and `um_export`.
- `EXT2_LOCK`, `EXT2_UNLOCK`, `EXT2_MTX`.
- `VFSTOEXT2`.
- `MNINDIR`, `blkptrtodb`, `is_sequential`.

Important interactions:
- Included by nearly every ext2fs implementation file.
- The mount lock protects shared filesystem/group accounting in allocation and related code.

Notable behavior:
- This is kernel-only under `_KERNEL`.
