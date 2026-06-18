# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/Makefile

Purpose: FreeBSD build makefile for the `pfctl` packet filter control utility.

Key behavior:
- Builds program `pfctl` in package `pf`.
- Installs configuration `pf.os` and manual page `pfctl.8`.
- Lists source files including parser, state printing, ALTQ, OS fingerprinting, radix, table, queue stats, optimizer, and ruleset code.
- Sets warning level and CFLAGS for prototypes, ALTQ, and include paths.
- Adds `WITH_INET6` and `WITH_INET` defines based on source build options.
- Links libraries `m`, `md`, and `pfctl`.
- Enables tests through `HAS_TESTS` and `SUBDIR.${MK_TESTS}+= tests`.

Dependencies:
- FreeBSD build system: `<src.opts.mk>` and `<bsd.prog.mk>`.
- `libpfctl` headers and object directory.
- Build options `MK_INET6_SUPPORT`, `MK_INET_SUPPORT`, and `MK_TESTS`.

Research notes:
- This file is outside nvmecontrol but still under the same FreeBSD source tree and subset A scope.
