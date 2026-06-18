# sources/storage-engines/wiredtiger/src/btree/bt_ovfl.c

Purpose: handles overflow item reads and removal/discard coordination. Overflow keys/values are stored as separate disk pages when too large for normal leaf cells; this file reads them safely and marks/free backs overflow blocks after reconciliation.

Important APIs/types/functions: static `__ovfl_read` performs the physical block-cache read and exposes the overflow payload. `__wt_ovfl_read` is the public read helper with removed-cell protection. `__wt_ovfl_remove` queues an overflow value for later discard. `__wt_ovfl_discard` flips on-page cell type to removed and frees backing blocks.

Control flow: reads go through `__wt_blkcache_read`, interpret the returned `WT_PAGE_HEADER`, and point the caller's `WT_ITEM` at `WT_PAGE_HEADER_BYTE`. If a page is supplied, `__wt_ovfl_read` takes the B-tree overflow read lock and returns a sentinel string rather than reading when the cell has already been reset to `WT_CELL_VALUE_OVFL_RM`. Removal during reconciliation is queued via `__wt_ovfl_discard_add`; after successful reconciliation, `__wt_ovfl_discard` unpacks the cell, takes the overflow write lock, atomically resets key/value overflow cell types to removed variants, releases the lock, and frees the blocks with `__wt_btree_block_free`.

State and persistence behavior: overflow removal mutates the in-memory disk image cell type so concurrent readers can detect removed overflow blocks. The backing disk blocks are freed only after reconciliation has safely copied required values to the history store when needed. Read statistics count overflow cache reads.

Dependencies and integration points: depends on block cache reads, B-tree overflow lock initialized in `bt_handle.c`, cell unpack/reset helpers, reconciliation's overflow discard queues, history-store preservation of old overflow values, and block-free APIs.

Risks: the main race is a reader reading an on-page overflow address while checkpoint/reconciliation frees and reuses the backing blocks. The per-B-tree overflow lock and cell-type transition are the protection. Returning `"WT_CELL_VALUE_OVFL_RM"` is a defensive path for a value that should not be read. Only key/value overflow raw types are legal in discard; anything else indicates corruption or caller error.

Test signals: synchronous overflow reads, read after value cell marked removed, reconciliation queue plus discard, key and value overflow type reset, block-free invocation, race tests with concurrent readers/checkpoint, and illegal cell type handling.
