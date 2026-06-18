# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/db/hash/compat_ndbmdatum.c

Builds compatibility versions of NDBM datum APIs using the old `datum12` layout.

It defines `__LIBC12_SOURCE__`, includes both modern `<ndbm.h>` and compatibility `<compat/include/ndbm.h>`, emits warnings for old `dbm_*` references, renames `datum` to `datum12`, and clamps datum sizes to `INT_MAX`.

It then includes the shared implementation `db/hash/ndbmdatum.c` under these compatibility definitions.
