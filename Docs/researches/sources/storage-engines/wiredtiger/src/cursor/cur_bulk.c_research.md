# sources/storage-engines/wiredtiger/src/cursor/cur_bulk.c

## Purpose
This file implements bulk cursor insert behavior for row-store and variable-length column-store btrees. Bulk cursors only support insert and close, and they optimize loading by assuming single-threaded, ordered, not-yet-visible input.

## Important APIs, Types, and Functions
Public functions are `__wti_curbulk_init` and `__wti_curbulk_close`. Local insert functions are `__curbulk_insert_var`, `__curbulk_insert_row`, `__curbulk_insert_row_skip_check`, plus error helpers `__bulk_col_keycmp_err` and `__bulk_row_keycmp_err`. Important types are `WT_CURSOR_BULK`, `WT_CURSOR_BTREE`, `WT_BTREE`, and scratch `WT_ITEM` buffers.

## Control Flow and Behavior
Initialization disables unsupported cursor methods, selects the insert method based on btree type and optional row-store sort-check skipping, marks the first insert, initializes record number state, allocates the `last` scratch buffer, and calls `__wt_bulk_init`.

Variable-length column inserts use append mode to synthesize sequential record numbers or require explicit increasing record numbers. They coalesce consecutive identical values by increasing the RLE count, emit skipped records as deleted runs, save the current value into `last`, and call `__wt_bulk_insert_var` when the previous run must be flushed. Row-store inserts require key/value, compare each key against the previous key with the btree collator unless sort-check skipping is configured, save the key, and call `__wt_bulk_insert_row`. Close wraps up the bulk load with `__wt_bulk_wrapup`, decrements the bulk cursor stat only on success, and frees the scratch buffer.

## State and Persistence
Bulk cursor state is transient until close: previous key/value, `first_insert`, `recno`, and RLE count. Persistent table contents are created through the underlying bulk-load machinery, and the data is not visible until the bulk cursor is closed successfully.

## Dependencies and Integration Points
The file depends on cursor API macros, key/value validation, btree type/collator, lower-level bulk insert/wrapup APIs, connection/data-source statistics, and scratch-buffer allocation.

## Risks
Risks include corruption from out-of-order keys when checks are skipped, incorrect RLE handling for zero-length values, record-number gaps not being represented as deletes, decrementing cursor stats only on successful close, and unsupported btree types falling through without an insert handler.

## Test Signals
Signals include ordered row bulk load success, out-of-order row/column errors, append-mode column load, skipped column records becoming deleted records, RLE compression for repeated values, skip-sort-check behavior, and close/wrapup error handling.
