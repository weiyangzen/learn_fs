# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_iconv/Makefile

## Scope

Builds the optional MSDOSFS iconv kernel module.

## Build Definition

- Sets `KMOD=msdos_iconv`.
- Builds `msdosfs_iconv.c`.
- Includes `<bsd.kmod.mk>`.

## Dependencies

Relies on the kernel module build system and iconv support declarations.

## Risks And Invariants

This submodule only provides iconv registration glue; actual filename conversion logic lives in the main MSDOSFS conversion file.
