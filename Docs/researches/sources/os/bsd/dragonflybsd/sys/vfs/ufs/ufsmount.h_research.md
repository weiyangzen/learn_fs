# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufsmount.h

## Purpose

Defines UFS mount arguments, MFS mount arguments, and the kernel-private `struct ufsmount` that stores per-mount UFS state.

## Main Structures

- `struct ufs_args`: mount arguments for UFS-based filesystems, including device path and export args.
- `struct mfs_args`: mount arguments for memory filesystems, including exported name, export args, base address, and size.
- `struct ufsmount`: per-mount state:
  - VFS mount pointer, device id, and device vnode.
  - FFS superblock pointer.
  - Quota vnodes, quota credentials, quota grace times, and quota flags.
  - Derived block mapping parameters: indirect pointers per block, block-pointer-to-disk-block shift, sequential increment.
  - Export state.
  - Saved max file size.
  - Inode allocation malloc type.
  - Effective-link-count validity flag.
  - Inode hash table and mask.

## Macros And Flags

- `QTF_OPENING`, `QTF_CLOSING`: quota transition flags.
- `VFSTOUFS(mp)`: casts `mnt_data` to `struct ufsmount`.
- `MNINDIR(ump)`: indirect pointers per block.
- `blkptrtodb(ump, b)`: converts UFS block pointer to disk blocks.
- `is_sequential(ump, a, b)`: tests physical sequentiality using `um_seqinc`.

## Dependencies And Integration Points

Included by UFS implementation files that need mount-private state. `ufs_bmap.c` relies on `MNINDIR`, `blkptrtodb`, and `is_sequential`; quota code relies on quota arrays and flags; inode hash code uses `um_ihashtbl` and `um_ihash`.

## Notes For Future Work

- Kernel-only contents are guarded by `_KERNEL`; user-visible mount argument structures are outside that guard.
- `um_i_effnlink_valid` lets code choose between softdep effective link counts and on-disk link counts.
