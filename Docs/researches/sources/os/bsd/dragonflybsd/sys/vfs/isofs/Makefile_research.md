# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/Makefile

Source read: complete file, 6 lines.

Purpose: Parent makefile for ISO filesystem modules.

Key contents:
- Sets `SUBDIR=cd9660`.
- Includes `<bsd.subdir.mk>`.

Integration:
- Delegates actual ISO 9660 module building to `sys/vfs/isofs/cd9660/Makefile`.

Risks and review notes:
- None beyond normal subdirectory build registration.
