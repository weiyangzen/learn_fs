# File Research: sources/os/bsd/netbsd-src/lib/libc/db/db/db.c

Implements the public `dbopen` dispatcher and panic-mode method replacement. `dbopen` validates open flags against allowed file flags and DB flags, then routes by `DBTYPE` to `__bt_open`, `__hash_open`, or `__rec_open`, passing through DB-specific flags separately from real `open(2)` flags.

The file also defines `__dbpanic`, used when an access method detects unrecoverable internal inconsistency. It replaces all operational DB methods except close with `__dberr`, making subsequent get/put/delete/seq/sync/fd calls fail with `RET_ERROR`.

Dependencies include `<db.h>` for the public DB structure and access method constants, and private open routines from btree/hash/recno compiled into libc.

Risks/invariants: `dbopen` rejects unsupported flag/type combinations with `EINVAL`. `__dbpanic` assumes `dbp` is valid and mutates function pointers in place, so callers holding a `DB *` see a permanently degraded handle until close.
