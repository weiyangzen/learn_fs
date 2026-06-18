# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_put.c

Read completely: 319 lines.

This implements btree insertion/replacement `__bt_put`. It validates flags/read-only state, stores oversized key/data values on overflow pages, handles cursor replacement, searches for the insertion point with a sorted-input fast path, enforces `R_NOOVERWRITE` and duplicate policy, deletes replaced leaf entries, splits full pages, inserts the new leaf item, updates cursor indexes, and marks the tree modified.

Important interactions: uses `__ovfl_put`, `__bt_search`, `__bt_dleaf`, `__bt_split`, and `bt_fast`. The sorted insertion cache tracks forward/backward append patterns through `bt_order` and `bt_last`.

Security/reliability notes: the source notes that if an insert fails after overflow pages are allocated, those overflow pages are not recovered. Page free-space calculations and split correctness are central to avoiding on-page corruption.
