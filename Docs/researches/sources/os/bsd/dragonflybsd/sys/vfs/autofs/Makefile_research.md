# File Research: sources/os/bsd/dragonflybsd/sys/vfs/autofs/Makefile

## Summary
Kernel module makefile for autofs.

## Main Responsibilities
- Sets `KMOD=autofs`.
- Builds `autofs.c`, `autofs_vfsops.c`, and `autofs_vnops.c`.
- Includes `bsd.kmod.mk`.

## Risks
The module depends on `autofs_vnops.c` even though that file is outside this grouped prompt; research of `autofs.c` and `autofs_vfsops.c` needs that context for node and VOP behavior.
