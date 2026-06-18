# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_put.c

Implements record insertion and replacement. `__rec_put` validates fixed-length record constraints, pads short fixed records with `bt_bval`, interprets `R_CURSOR`, `R_SETCURSOR`, `R_IAFTER`, `R_IBEFORE`, `R_NOOVERWRITE`, and default replacement/append semantics, imports backing-file records as needed, fills skipped records with empty or padded records, calls `__rec_iput`, updates cursor state, marks recno modified, and returns the resulting record number.

`__rec_iput` performs the actual btree insertion/replacement. It stores oversized record data in btree overflow pages, searches for the insertion/replacement leaf with `__rec_search`, deletes an existing record unless doing before/after insertion, splits the page through `__bt_split` when necessary, otherwise shifts line pointers, writes an `RLEAF`, increments `bt_nrecs`, marks the tree modified, and releases the page dirty.

Dependencies include overflow handling, `__rec_search`, `__rec_dleaf`, `__bt_split`, and recno/btree page macros.

Risks/invariants: if overflow allocation succeeds but a later insert fails, comments note those pages are not recovered. External keys are one-based; insertion into gaps creates synthetic records.
