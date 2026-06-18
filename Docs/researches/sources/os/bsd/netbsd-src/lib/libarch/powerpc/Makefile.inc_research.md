# File Research: sources/os/bsd/netbsd-src/lib/libarch/powerpc/Makefile.inc

Build fragment for PowerPC libarch subdirectories.

Key behavior:
- Includes `<bsd.own.mk>`.
- Adds `powerpc/espresso` as a subdir only for `MACHINE=evbppc` and `MACHINE_ARCH=powerpc`.

Dependencies:
- NetBSD machine selection variables.
