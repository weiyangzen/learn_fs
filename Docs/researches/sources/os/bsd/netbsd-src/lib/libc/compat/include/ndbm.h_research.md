# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/ndbm.h

Defines the old `datum12` NDBM data structure.

`datum12` stores `void *dptr` and `int dsize`; the header declares old `dbm_delete`, `dbm_fetch`, `dbm_firstkey`, `dbm_nextkey`, and `dbm_store`.

This preserves the older database record ABI.
