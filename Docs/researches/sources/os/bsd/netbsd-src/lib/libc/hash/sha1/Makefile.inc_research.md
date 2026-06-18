# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/sha1/Makefile.inc

Build fragment for SHA1 support.

Adds:
- Path `${.CURDIR}/hash/sha1`.
- Sources `sha1.c`, `sha1hl.c`.
- Manpage `sha1.3`.
- Manpage links for `SHA1Init`, `SHA1Update`, `SHA1Final`, high-level helpers, and `SHA1Transform`.
