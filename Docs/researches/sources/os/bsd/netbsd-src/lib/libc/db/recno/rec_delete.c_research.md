# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_delete.c

Implements record deletion. `__rec_delete` validates flags and record numbers, supports explicit-key deletion and `R_CURSOR`, unpins retained pages, and delegates to `rec_rdelete`. On success it marks both btree and recno state modified.

`rec_rdelete` finds the zero-based record with `__rec_search(..., SDELETE)`, which decrements internal subtree counts during descent, then removes the leaf entry with `__rec_dleaf`.

`__rec_dleaf` deletes one `RLEAF` entry from a leaf page, frees overflow data if present, compacts payload bytes and line pointers, updates page bounds, and decrements `bt_nrecs`. Empty pages are not reclaimed, but become usable for future inserts.

Dependencies include recno search/count maintenance, btree overflow deletion, page layout macros, and mpool dirty-page handling.

Risks/invariants: internal count updates happen before leaf deletion; `__rec_search` contains recovery logic for descent errors, but failures after leaf mutation can still leave higher-level state sensitive.
