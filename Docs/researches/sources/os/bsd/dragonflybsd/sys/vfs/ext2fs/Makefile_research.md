# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/Makefile

Read completely: 8 lines.

## Role

This Makefile defines the DragonFlyBSD ext2fs kernel module build.

## Main Contents

- Sets `KMOD= ext2fs`.
- Lists ext2fs module source files:
  - allocation and block mapping
  - checksum and extents
  - hash/htree support
  - inode, lookup, subroutines, VFS ops, and vnode ops
- Adds generated/config option header `opt_suiddir.h`.
- Includes the common kernel module build rules with `.include <bsd.kmod.mk>`.

## Research Notes

- No runtime logic is present.
- Build correctness depends on the listed source set matching the ext2fs module implementation dependencies.
