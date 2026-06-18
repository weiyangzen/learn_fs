# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_delete.c

Read completely: 641 lines.

This implements btree deletion. `__bt_delete` handles key deletion and cursor deletion, rejects writes to read-only trees, and marks the tree modified. The helpers delete all duplicates for a key, delete individual leaf items, free overflow chains, relink and free empty pages, collapse root pages back to empty leaves, and adjust cursor state around deleted records.

Important interactions: relies on `__bt_search` to build the parent stack, `__bt_dleaf` for leaf compaction, `__ovfl_delete` for large key/data storage, and mpool for page pinning. Cursor deletion may need `__bt_stkacq` to rebuild the stack when deleting an item from a page found by sequential scan.

Security/reliability notes: mutation is intricate and assumes page metadata and parent stack consistency. A noted edge is old-style page compaction and index adjustment; corrupt page offsets would be dangerous if not filtered earlier.
