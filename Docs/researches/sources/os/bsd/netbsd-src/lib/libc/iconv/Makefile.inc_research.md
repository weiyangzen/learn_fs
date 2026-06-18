# File Research: sources/os/bsd/netbsd-src/lib/libc/iconv/Makefile.inc

Build fragment for libc iconv support.

Adds:
- Path `${ARCHDIR}/iconv ${.CURDIR}/iconv`.
- Source `iconv.c`.
- Manpage `iconv.3` with links for `iconv_open.3` and `iconv_close.3`.
- Extra include path `-I${LIBCDIR}/citrus` for Citrus conversion internals.
