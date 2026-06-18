# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_seq.c

Provides the btree sequential scan implementation behind `DB->seq`. `__bt_seq` accepts `R_CURSOR`, `R_FIRST`, `R_LAST`, `R_NEXT`, `R_PREV`, `R_RNEXT`, and `R_RPREV`, unpins any page retained from a previous call, initializes or advances the cursor, records the cursor position with `__bt_setcur`, and returns data through `__bt_ret`.

`__bt_seqset` positions scans at a keyed lower-bound, first record, or last record by walking the left or right side of the tree. `__bt_seqadv` advances from the saved cursor and handles deleted-cursor states (`CURS_ACQUIRE`, `CURS_AFTER`, `CURS_BEFORE`). The `R_RNEXT`/`R_RPREV` variants use `__bt_rseq_next` and `__bt_rseq_prev` to traverse by parent stack rather than sibling leaf links.

`__bt_first` finds the first record greater than or equal to a key, walking backward across duplicates so duplicate scans start at the earliest matching entry. `__bt_setcur` clears any saved deleted key and updates the cursor page/index.

Dependencies include `__bt_search`, `__bt_cmp`, `__bt_ret`, the mpool page cache, and cursor/stack definitions in `btree.h`.

Risks/invariants: the code relies on pinned-page lifetime when `B_DB_LOCK` is not set. Comments document duplicate-key anomalies after cursor replacement via delete/add pairs.
