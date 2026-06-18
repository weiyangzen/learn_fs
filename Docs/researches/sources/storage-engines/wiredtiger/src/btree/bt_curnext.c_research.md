# sources/storage-engines/wiredtiger/src/btree/bt_curnext.c

## Purpose
Implements forward btree cursor traversal for row-store and variable-length column-store pages. It walks insert lists, on-page cells, append lists, page boundaries, bounds, transaction visibility, prepare-conflict retry state, diagnostic key-order checks, and opportunistic eviction of pages with many deleted entries.

## Important APIs, types, and functions
- `__wt_btcur_next` is the public btree-cursor next implementation.
- `__cursor_row_next` iterates row-store insert slots and on-page rows in a unified slot namespace.
- `__cursor_var_next` iterates standard variable-length column-store records.
- `__cursor_var_append_next` iterates column-store append lists.
- `__wti_btcur_iterate_setup` initializes direction-independent iteration state after search or direction changes.
- Diagnostic builds add `__wti_cursor_key_order_check`, `__wt_cursor_key_order_init`, and `__wt_cursor_key_order_reset`.

## Control flow
`__wt_btcur_next` clears external key/value flags, initializes the cursor operation, optionally positions an unpositioned bounded cursor at its lower bound, initializes iteration state if changing direction, and then loops through the current page before walking to the next leaf. Column append lists are handled before normal column cells. Row traversal alternates odd insert-list slots and even on-page row slots. Column traversal advances record numbers through RLE cells, checks matching update insert lists, and skips large deleted RLE ranges by jumping to the next possible visible record.

Each candidate key is checked against upper bounds, then visibility is evaluated through `__wt_txn_read_upd_list` for insert/update lists or `__wt_txn_read` for on-page/history-store values. Tombstones and invalid updates are skipped, visible values are returned, and `WT_CURSTD_KEY_ONLY` can short-circuit value reads. If a page is exhausted, next may mark heavily deleted pages dirty and evict soon, then walks with snapshot-page skipping when possible.

## State and persistence behavior
This file updates cursor iteration fields such as `recno`, `slot`, `row_iteration_slot`, `ins_head`, `ins`, append/iterate flags, retry flags, cached RLE state, and diagnostic last-key state. It does not persist data directly, but it can mark pages dirty/evict-soon when traversal observes many globally visible tombstones so reconciliation can discard obsolete content. Read statistics and skip counters are updated.

## Dependencies and integration points
Forward traversal depends on row/column page formats, insert skip lists, transaction visibility and history-store reads, cursor bounds helpers in `bt_cursor.c`, tree walking, eviction, diagnostic debug tree dumps, collators, and page-skip helpers for snapshot isolation.

## Risks and edge cases
- RLE deleted ranges can be huge; the skip-jump logic is critical for performance and must not skip visible inserts.
- Prepare conflicts preserve retry state so user retry can continue from the same logical position.
- Direction changes rely on `__wti_btcur_iterate_setup` to map row-store positions into the shared slot namespace.
- Bounds positioning can return a record directly or require walking; diagnostic assertions verify lower-bound assumptions.
- Read-uncommitted traversal can observe out-of-order effects across page boundaries, so diagnostic order checks are reset in that case.

## Test signals
Tests should cover row and column next traversal, append lists, RLE values and deleted RLE gaps, insert-list visibility, tombstones, key-only cursors, lower/upper bounded next, prepare-conflict retry, direction changes with prev, snapshot page skipping, read-once `WT_READ_WONT_NEED`, deleted-page eviction triggers, and diagnostic key-order checks.
