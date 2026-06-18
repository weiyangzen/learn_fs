# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_seq.c

Implements recno sequential scans. `__rec_seq` handles `R_CURSOR`, `R_FIRST`, `R_LAST`, `R_NEXT`, and `R_PREV`, using `bt_cursor.rcursor` as a one-based current record number. It unpins any page retained from a previous call, computes the target record number, lazily imports backing-file records if needed, searches with `__rec_search`, initializes the cursor, and returns key/data via `__rec_ret`.

`R_LAST` forces full import of the backing file when EOF is not known, because the last record number is unknown until import completes. `R_NEXT` and `R_PREV` require an initialized cursor or fall through to first/last behavior.

Dependencies include recno lazy import callback `bt_irec`, `__rec_search`, `__rec_ret`, and mpool pin management.

Risks/invariants: end-of-file and in-memory flags determine whether missing records are final or trigger import. As elsewhere, page retention depends on `B_DB_LOCK`.
