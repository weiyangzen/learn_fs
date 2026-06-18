# File Research: sources/os/bsd/netbsd-src/lib/libc/db/mpool/Makefile.inc

Build fragment for the memory-pool page cache. It adds `${.CURDIR}/db/mpool` to `.PATH` and appends `mpool.c` to `SRCS`.

Dependencies: included by libc DB build; btree/recno use mpool for page caching.

Risks/invariants: minimal; only one implementation file is listed.
