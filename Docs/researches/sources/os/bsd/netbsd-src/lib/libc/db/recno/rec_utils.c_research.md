# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_utils.c

Provides `__rec_ret`, the recno return-value builder. It copies the one-based record number into `bt_rkey` when a key is requested, because recno keys are implicit and not stored on leaf pages. For data, it loads overflow payloads through `__ovfl_get`, copies ordinary data into `bt_rdata` when `B_DB_LOCK` is set, or returns a direct pointer into the pinned `RLEAF` otherwise.

Dependencies include `GETRLEAF`, `RLEAF`, overflow helpers, and `BTREE` return buffers.

Risks/invariants: direct data pointers require the page to remain pinned by the caller. The function uses reusable buffers in `BTREE`, so returned copied data is overwritten by later DB operations on the same handle.
