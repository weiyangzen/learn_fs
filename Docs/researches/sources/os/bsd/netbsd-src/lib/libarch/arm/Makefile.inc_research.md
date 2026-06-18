# File Research: sources/os/bsd/netbsd-src/lib/libarch/arm/Makefile.inc

Build fragment for ARM libarch support.

Key behavior:
- Includes `<bsd.own.mk>`.
- Defaults `LIBC_MACHINE_CPU` to `${MACHINE_CPU}`.
- Adds `arm_sync_icache.c` and `arm_drain_writebuf.c` only when `${LIBC_MACHINE_CPU} == "arm"`.
- Always installs manpage entries `arm_sync_icache.2` and `arm_drain_writebuf.2`.

Dependencies:
- NetBSD make conditionals and shared libarch build variables.
