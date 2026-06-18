# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_search.c

Implements btree keyed lookup. `__bt_search` descends from `P_ROOT`, binary-searching each page with `__bt_cmp`, maintaining `t->bt_cur` as the returned pinned page/index and `bt_stack` as the parent path needed by insertion and splitting. On internal pages it selects the child from the largest separator key less than or equal to the search key; on leaf pages it returns either an exact match or the insertion slot.

The duplicate-key path is the important special case. When duplicates are allowed and the computed leaf slot lies at a page boundary, `__bt_sprev` and `__bt_snext` inspect the adjacent leaf to recover exact matches that may have migrated across page boundaries after deletion. Those helpers also repair the saved parent stack by walking upward and then downward so later split/insert code still has the correct ancestry.

Dependencies include `mpool_get`/`mpool_put`, `PAGE`, `BINTERNAL`, `EPG`, `BT_PUSH`, `BT_POP`, and `GETBINTERNAL` from `btree.h`, plus `__bt_cmp` from `bt_utils.c`.

Risks/invariants: returned `EPG->page` is intentionally pinned; callers must release it. The fixed-size parent stack is assumed deep enough. Error paths can leave stack state partially adjusted, so callers generally treat `NULL` as hard failure.
