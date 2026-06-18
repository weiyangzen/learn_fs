# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/sha2/Makefile.inc

Build fragment for SHA2 support.

Adds:
- Path `${.CURDIR}/hash/sha2`.
- Sources `sha2.c`, `sha224hl.c`, `sha256hl.c`, `sha384hl.c`, `sha512hl.c`.
- Manpage `sha2.3`.
- Extensive manpage links for SHA224/SHA256/SHA384/SHA512 init, update, final, end, file, data, transform, and file chunk helpers.
