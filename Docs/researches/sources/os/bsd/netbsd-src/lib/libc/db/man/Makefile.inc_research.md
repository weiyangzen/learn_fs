# File Research: sources/os/bsd/netbsd-src/lib/libc/db/man/Makefile.inc

Build fragment for DB manual pages. It adds `${.CURDIR}/db/man` to `.PATH`, installs `btree.3`, `dbm_clearerr.3`, `dbopen.3`, `hash.3`, `recno.3`, and `mpool.3`, and defines manual links for ndbm, dbopen/db, and mpool entry points.

Dependencies: libc manpage build machinery.

Risks/invariants: documentation link names must track public function names exported by the DB and mpool implementations.
