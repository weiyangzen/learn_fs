# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_iconv/Makefile

Source read: complete file, 6 lines.

Purpose: Kernel module makefile for cd9660 iconv support.

Key contents:
- Sets `KMOD= cd9660_iconv`.
- Builds `cd9660_iconv.c`.
- Includes `<bsd.kmod.mk>`.

Integration:
- Built as a submodule from the parent cd9660 makefile.

Risks and review notes:
- Module usefulness depends on the kernel iconv framework being available.
