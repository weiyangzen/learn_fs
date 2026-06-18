# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/extern.h

Declares private recno functions and includes the btree private declarations. The API covers DB method implementations (`__rec_close`, `__rec_delete`, `__rec_fd`, `__rec_get`, `__rec_put`, `__rec_seq`, `__rec_sync`), leaf deletion/return helpers, record insertion, record-number search, and backing-file import/export functions for fixed and variable records via mmap or pipe/file streams.

Dependencies: requires `BTREE`, `PAGE`, `EPG`, `DB`, `DBT`, `recno_t`, and `enum SRCHOP`.

Risks/invariants: recno is not independent; it mutates and reuses btree internals while changing DB method pointers after `__bt_open`.
