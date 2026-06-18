# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_iconv/msdosfs_iconv.c

## Scope

Registers iconv support for MSDOSFS as a small kernel module.

## APIs And Behavior

- Includes kernel, module, mount, and iconv headers.
- Invokes `VFS_DECLARE_ICONV(msdos)` to declare/register the iconv integration used by MSDOSFS mount and filename conversion paths.

## Dependencies

Depends on DragonFly kernel module infrastructure and iconv framework macros.

## Risks And Invariants

This file contains no conversion logic itself. The main MSDOSFS code expects the registered iconv hooks to exist when the filesystem is mounted with kernel iconv support enabled.
