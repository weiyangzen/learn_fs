# File Research: sources/os/bsd/netbsd-src/lib/libarch/m68k/Makefile.inc

Build fragment for m68k libarch support.

Key behavior:
- When `${MACHINE_CPU} == "m68k"`, disables lint and sets `SRCS` to `m68k_sync_icache.S`.
- Adds `m68k_sync_icache.2` to installed manpages.

Dependencies:
- NetBSD make variables for CPU selection.
