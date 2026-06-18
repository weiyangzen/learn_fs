# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/ndbmdatum.c

Implements datum-oriented `ndbm` operations using the underlying `DB` methods. `dbm_fetch` maps a `datum` key to `DBT`, calls `get`, and returns a null datum on failure. `dbm_firstkey` and `dbm_nextkey` call `seq` with `R_FIRST` and `R_NEXT`. `dbm_delete` calls `del` and translates any nonzero status to `-1`. `dbm_store` calls `put`, mapping `DBM_INSERT` to `R_NOOVERWRITE`.

Dependencies include `<ndbm.h>`, `DBT`, DB method pointers, and `datum_truncate`, which can be overridden by platform headers to fit old `datum.dsize` width.

Risks/invariants: returned data/key pointers are those provided by the hash method and are valid only according to DB method lifetime rules. The API compresses DB status values into older ndbm conventions, losing some distinction between not-found and internal errors.
