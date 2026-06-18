# sources/storage-engines/wiredtiger/src/btree/bt_stat.c

## Purpose

`bt_stat.c` initializes and gathers btree data-source statistics. It reports btree configuration, cache footprint, reconciliation delta averages, optional cache-walk stats, and optional tree-walk counts for page types, entries, overflow items, deleted column records, RLE expansion, and empty row values. The complete 347-line source was read.

## Important APIs, Types, and Functions

`__wt_btree_stat_init` is the exported statistics initializer. It calls block-manager stats, sets btree/cache/reconciliation counters, and optionally runs cache and tree walks. `__stat_tree_walk` traverses pages and dispatches to `__stat_page`. Page counters are implemented by `__stat_page_col_var`, `__stat_page_row_int`, and `__stat_page_row_leaf`.

## Control Flow

`__wt_btree_stat_init` fills static btree settings, dirty/in-use cache byte counters, pre-compression page limits, and average delta chain lengths with zero-denominator guards. If requested, it invokes eviction cache stat walking and then a btree tree walk.

`__stat_tree_walk` clears tree-derived counters, walks pages with `WT_READ_INTERNAL_OP | WT_READ_VISIBLE_ALL | WT_READ_WONT_NEED`, counts each page under `WT_WITH_PAGE_INDEX`, releases the final page, and maps `WT_NOTFOUND` to success. Column variable pages count base cells, RLE, stop-time deletes, overflow cells, cell update lists, and append inserts. Row internal pages count overflow keys from disk images. Row leaves count insert lists, on-page rows adjusted by updates and stop timestamps, overflow values, overflow keys, and zero-length values inferred from disk cells.

## State and Persistence Behavior

The file does not change persistent btree contents. It writes `WT_DSRC_STATS` counters and may read pages into cache for tree-walk statistics; those reads are marked `WT_READ_WONT_NEED` to reduce cache pollution. Counts are snapshots and may be approximate under concurrent updates.

## Dependencies and Integration Points

Dependencies include block-manager stats, cache accounting, eviction cache stat walk, tree walking/page-in, page-index protection, cell unpacking, row/column page macros, insert skip lists, update types, and statistics macros such as `WT_STATP_DSRC_SET` and `WT_STATP_DSRC_INCRV`.

## Risks and Edge Cases

Stats can race with concurrent modifications and should not be treated as transactional counts. VLCS RLE plus updates is approximate. Overflow-key and empty-value detection requires a disk image. Incorrect update-type filtering can skew live/deleted entry counts. Tree-walk cleanup must release the last page even on errors to avoid hazard leaks.

## Test Signals

Cover stats with and without tree-walk mode, row and column btrees, RLE and tombstone cases, insert and append lists, reserve/standard/modify updates, stopped time windows, overflow keys and values, empty row values, delta average denominators, and injected tree-walk/page-read errors.
