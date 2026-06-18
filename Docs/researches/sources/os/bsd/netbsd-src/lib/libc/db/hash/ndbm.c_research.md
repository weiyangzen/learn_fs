# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/ndbm.c

Implements part of the `ndbm` compatibility API on top of the hash access method. `dbm_open` appends `DBM_SUFFIX` to the supplied base path, configures a small `HASHINFO`, converts write-only opens to read/write because hash needs reads, and calls `__hash_open`.

`dbm_close` calls the underlying DB close method. `dbm_error` and `dbm_clearerr` expose/reset `HTAB.err`. `dbm_dirfno` returns the hash file descriptor.

Dependencies: `<ndbm.h>`, hash internals, and the hash DB method table.

Risks/invariants: `strncpy`/`strncat` build the suffixed path in a fixed `MAXPATHLEN` buffer; very long input truncates rather than returning `ENAMETOOLONG`. The DBM handle is cast from `DB *`, relying on ABI compatibility between the old wrapper type and the DB structure.
