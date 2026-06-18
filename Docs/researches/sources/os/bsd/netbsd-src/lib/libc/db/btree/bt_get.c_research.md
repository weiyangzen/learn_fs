# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_get.c

Read completely: 104 lines.

This implements btree lookup `__bt_get`. It unpins any previous page, rejects nonzero flags, searches for the key, returns `RET_SPECIAL` if not exact, and uses `__bt_ret` to return the data.

Important interactions: if `B_DB_LOCK` is set, returned key/data are copied and the page is unpinned; otherwise the found page remains pinned across calls via `bt_pinned`.

Security/reliability notes: page pin lifetime is part of the DB API contract. Callers must not assume returned data outlives the next DB operation unless copied.
