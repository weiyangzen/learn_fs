# File Research: sources/os/bsd/netbsd-src/lib/libc/db/db/Makefile.inc

Build fragment for the generic DB layer. It adds `${.CURDIR}/db/db` to `.PATH` and appends `db.c` and `dbfile.c` to `SRCS`.

Dependencies: consumed by the libc DB build and paired with subdirectory Makefile fragments for btree, hash, mpool, recno, and man pages.

Risks/invariants: minimal; source names here must match the generic DB dispatch and file-helper implementation files.
