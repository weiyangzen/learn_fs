# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/db/hash/Makefile.inc

Build fragment for compatibility hash database code.

It adds `${COMPATDIR}/db/hash` to `.PATH` and adds `compat_ndbmdatum.c` to `SRCS`.

This wires old NDBM datum compatibility into libc.
