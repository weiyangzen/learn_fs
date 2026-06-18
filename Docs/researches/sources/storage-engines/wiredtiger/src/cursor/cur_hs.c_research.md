# sources/storage-engines/wiredtiger/src/cursor/cur_hs.c

## Purpose
`cur_hs.c` implements WiredTiger history-store cursors. These cursors wrap an underlying file cursor on the history-store table, expose a history-store-specific key/value API, apply visibility filtering over time windows, support history-store insert/update/remove/range-truncate operations, and handle multiple history-store IDs for disaggregated storage.

## Important APIs, Types, and Functions
The exported API includes `__wt_curhs_open`, `__wt_curhs_open_ext`, `__wt_curhs_cache`, `__wt_curhs_get_cached`, `__wt_curhs_next_hs_id`, `__wt_curhs_search_near_before`, `__wt_curhs_search_near_after`, `__wt_curhs_range_truncate`, `__wt_curhs_get_btree_id`, and `__wt_curhs_set_btree_id`. `__wt_curhs_open_ext` builds a `WT_CURSOR_HS` with history-store key/value formats and an underlying file cursor opened by `__curhs_file_cursor_open`.

`__curhs_set_key` accepts a variable argument count containing btree ID, optional datastore key, optional start timestamp, and optional counter. It records which pieces are set with `WT_HS_CUR_*` flags and sets the underlying file cursor key. `__curhs_set_value` stores a `WT_TIME_WINDOW` and sets the encoded history-store value fields. `__curhs_next_visible` and `__curhs_prev_visible` are the central visibility filters.

## Control Flow
Underlying file cursor operations run at `WT_ISO_READ_UNCOMMITTED` via `__curhs_file_cursor_next`, `prev`, and `search_near`, then the history-store wrapper filters records according to btree ID, datastore key, and time-window visibility. `next` and `prev` advance the file cursor, call the appropriate visible-skip loop, and expose the file cursor key/value buffers through the history-store cursor. `search_near` handles both directions: it first lands near the encoded key, tries visible records on the initial side, then crosses back through the requested key or btree range if needed.

Insert builds one or two `WT_UPDATE` structures. The standard update is stamped with the start time point; if the time window has a stop point, a tombstone stamped with the stop time is linked before it. The code searches the history-store btree and calls `__wt_hs_modify`, retrying on `WT_RESTART`. Update is a specialized operation that adds a stop timestamp to an existing positioned history-store record. Remove adds an un-timestamped tombstone through `__curhs_remove_int`. Range truncate maps history-store cursors to their underlying file cursors and calls `__wt_cursor_truncate`.

## State and Persistence Behavior
The history-store cursor itself owns transient state: selected `btree_id`, `hs_id`, datastore-key scratch buffer, `WT_TIME_WINDOW`, and key-selection flags. Persistent history data is stored in history-store btrees through update chains, not by this wrapper directly. Visibility behavior deliberately differs from ordinary file cursors: the file cursor reads uncommitted, while this layer decides whether to return all records, non-obsolete committed records, or records visible to the current transaction snapshot. Globally visible tombstones are skipped during reads because newer historical records for the same key may still be needed.

## Dependencies and Integration Points
The file integrates with reconciliation (`rec_hs.c` and `rec_write.c`), rollback-to-stable (`rts_history.c` and `rts_btree.c`), transaction code, history-store verification, btree read/delete paths that pre-cache history-store cursors, schema truncate routing, statistics, and disaggregated shared history-store URIs. It also cooperates with checkpoint cursors by propagating the session's selected history-store checkpoint name or a stable checkpoint URI suffix.

## Risks and Edge Cases
The highest risks are visibility and range-boundary mistakes. The cursor must not leak records from another btree ID unless `WT_CURSTD_HS_READ_ACROSS_BTREE` is set, and `btree_id + 1` is allowed only for truncation stop keys. Search-near must handle concurrent inserts, packed-key ordering differences between datastore keys and history-store keys, and both before/after helper semantics. Insert/update own update memory only until `__wt_hs_modify` succeeds. Disaggregated mode restricts writes to leader-owned history-store btrees. Cursor caching avoids metadata, recovery, no-reconcile, and default-session cases to prevent deadlocks or unsafe handle sweeping.

## Test Signals
History-store cursor behavior is exercised by reconciliation, rollback-to-stable, history-store verification, transaction cleanup, and format's `ops.hs_cursor` path. `test/format/hs.c` directly iterates history-store IDs and opens history-store cursors. Useful targeted tests include visible-skip behavior with globally visible tombstones, `search_near_before/after` across btree boundaries, checkpoint history-store cursor reads, disaggregated shared/private history-store ID mapping, and range truncation with explicit stop cursors.
