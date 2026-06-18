# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_split.c

Implements btree and recno page splitting. `__bt_split` splits a full leaf or internal page, inserts the pending item into the chosen half, then walks the saved parent stack to insert separator entries and propagate splits up to the root. It supports both btree leaf/internal entries and recno leaf/internal count entries.

`bt_page` splits non-root pages, allocates a right page, fixes sibling links, and has an append optimization for sorted right-edge inserts. `bt_root` allocates new left/right children for root splits. `bt_broot` and `bt_rroot` rewrite the root as a btree or recno internal page, respectively. `bt_psplit` copies page entries into left/right pages around a skipped insertion slot and adjusts any initialized cursor that pointed at the original page.

For btree internal separators, the file can use prefix compression via `bt_pfx`, and `bt_preserve` marks overflow key chains that become referenced from internal pages so deletion of the leaf copy does not reclaim them. For recno, parent entries are updated with `NEXTINDEX` or `rec_total` counts.

Dependencies include page layout macros from `btree.h`, overflow-page helpers, `mpool`, and the search stack populated by `bt_search.c` or `rec_search.c`.

Risks/invariants: a failure while propagating parent splits can leave the tree inconsistent; the code calls `__dbpanic` after releasing pins. Overflow pages allocated before later insert failure may not always be recovered.
