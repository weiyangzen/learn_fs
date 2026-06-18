# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/Makefile

## Scope

Builds the main DragonFlyBSD MSDOSFS kernel module and its iconv submodule.

## Build Definition

- Sets `KMOD=msdos`.
- Builds conversion, denode, FAT, lookup, VFS, vnode, and option sources.
- Exports `msdos_iconv`.
- Descends into `msdosfs_iconv`.
- Includes `<bsd.kmod.mk>`.

## Dependencies

Relies on the kernel module build system and adjacent MSDOSFS sources not all included in this group.

## Risks And Invariants

The main module exports iconv linkage expected by the optional iconv module and conversion code.
