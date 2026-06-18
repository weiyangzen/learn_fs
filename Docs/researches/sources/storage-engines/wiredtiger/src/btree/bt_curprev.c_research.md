# sources/storage-engines/wiredtiger/src/btree/bt_curprev.c

## Purpose
Implements reverse btree cursor traversal for row-store and variable-length column-store pages. It mirrors `bt_curnext.c` but adds reverse skip-list navigation, descending row-slot traversal, upper-bound positioning, lower-bound early exits, and reverse-specific prepare retry and diagnostic ordering behavior.

## Important APIs, types, and functions
- `__wt_btcur_prev` is the public btree-cursor previous implementation.
- `__cursor_skip_prev` moves backwards through an insert skip-list finger using search stacks.
- `__cursor_row_prev` iterates row-store insert and on-page entries backward.
- `__cursor_var_prev` iterates variable-length column-store records backward.
- `__cursor_var_append_prev` iterates column append lists backward.
- It reuses iteration setup and diagnostic key-order helpers from `bt_curnext.c`.

## Control flow
`__wt_btcur_prev` initializes cursor state, optionally positions an unpositioned bounded cursor at its upper bound, sets reverse tree-walk flags, and loops over append lists, current page content, and previous pages. On each page, column append entries are considered first when entering a new page. Standard column traversal decrements record numbers, searches the matching column cell, checks insert-list updates, reads on-page/history values, and jumps over deleted RLE ranges using the prior visible insert or RLE start. Row traversal descends the shared row iteration slot namespace and uses `__cursor_skip_prev` to move through insert lists.

`__cursor_skip_prev` reconstructs or adjusts the skip-list search stack so it points before the current insert. It uses acquire barriers to avoid weak-memory-order races with concurrent insert publication and restarts if the stack becomes inconsistent.

## State and persistence behavior
Reverse traversal updates the same cursor fields as forward traversal but in descending order. It tracks `page_deleted_count`, total skipped records, retry flags, append iteration flags, RLE cache state, and diagnostic last-key state. It can mark pages dirty and evict soon after encountering many globally visible tombstones, indirectly causing future reconciliation to clean obsolete content.

## Dependencies and integration points
The file depends on insert-list skip-stack conventions established by search, row/column page accessors, transaction visibility, history-store reads, bounds comparison/positioning, tree walk with `WT_READ_PREV`, eviction/page-dirty helpers, and diagnostic key-order helpers from next traversal.

## Risks and edge cases
- Reverse skip-list walking is concurrency-sensitive; acquire barriers and restart paths are essential to avoid skipping inserts.
- Deleted RLE jump logic must choose the largest update below the current record or the RLE start boundary.
- Bounds and prepare conflict handling differ subtly from forward traversal; retry flags must be cleared in the opposite direction.
- Row reverse traversal instantiates row leaf keys before walking a new page, which can add cost but is needed for backward key access.
- As with next, read-uncommitted isolation can require diagnostic order-check resets across page boundaries.

## Test signals
Tests should cover reverse row and column traversal, reverse append-list traversal, skip-list concurrent insert races, deleted RLE gap skipping, lower/upper bounded prev, prepare-conflict retry and direction switches, key-only cursors, snapshot page skipping, deleted-page eviction triggers, and diagnostic order checking.
