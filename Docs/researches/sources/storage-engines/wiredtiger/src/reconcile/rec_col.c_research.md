<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/reconcile/rec_col.c -->
# sources/storage-engines/wiredtiger/src/reconcile/rec_col.c

## Purpose
Reconciles column-store pages, including bulk variable-length inserts, column internal pages, and variable-length column-store leaf pages.

## Important APIs, Types, and Functions
`__wt_bulk_insert_var`, `__wti_rec_col_int`, and `__wti_rec_col_var` are the main entry points. Helpers include `__rec_col_merge` and `__rec_col_var_helper`.

## Control Flow
Bulk insert builds delete or value cells, optionally dictionary-compresses, copies into the reconciliation image, updates time aggregates, and advances record numbers. Internal reconciliation walks child refs, asks `__wti_rec_child_modify` for state, merges multiblock children, builds/copies address/proxy cells, updates aggregates, and splits as needed. VLCS leaf reconciliation walks on-page RLE cells and append lists, selects visible updates, reconstructs modifies, handles stale values/tombstones, manages overflow reuse/removal, coalesces equal adjacent values into RLE runs, and writes the final split image.

## State and Persistence Behavior
Produces new disk images and parent time aggregates. It removes unused overflow blocks, clears stale on-disk values, may clear history-store entries for no-timestamp tombstones, and can convert all-deleted pages to empty namespace gaps when safe.

## Dependencies and Integration Points
Depends on update selection, time windows, dictionary replacement, split machinery, overflow management, history-store cleanup, salvage cookies, column insert lists, and child reconciliation.

## Risks and Edge Cases
VLCS gaps, UINT64_MAX record numbers, overflow values reused across RLE entries, skipped aborted prepared updates, and salvage trimming are all delicate. Prepared preservation asserts prevent leaking on-page prepared updates.

## Test Signals
Column-store reconciliation tests should cover RLE coalescing, append gaps, overflow reuse/removal, modify reconstruction, no-timestamp tombstone cleanup, salvage, all-deleted page emptying, and prepared-preserve scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/reconcile/rec_col.c -->
