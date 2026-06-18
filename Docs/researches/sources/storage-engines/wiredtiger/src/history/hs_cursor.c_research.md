# sources/storage-engines/wiredtiger/src/history/hs_cursor.c

## Purpose
This file provides low-level operations for modifying, reading, reconstructing, and truncating history-store records. It is central to timestamped reads that need older values, rollback/recovery code that manipulates HS content, and cleanup paths that remove all history for a btree id.

## Important APIs, Types, And Functions
`__wt_hs_modify` writes a supplied `WT_UPDATE` into the HS using `__wt_row_modify` directly on a `WT_CURSOR_BTREE`, bypassing the ordinary cursor API because HS updates must be immediately visible and do not follow normal transaction semantics. `__wt_hs_upd_time_window` exposes the `WT_TIME_WINDOW` from a positioned HS cursor's `upd_value`. `__wt_hs_find_upd` searches the HS for the visible historical update for a row key or column-store recno and fills a `WT_UPDATE_VALUE`. `__wt_hs_btree_truncate` deletes the contiguous HS key range for a given btree id using start and stop HS cursors and `WT_SESSION::truncate`.

## Control Flow
`__wt_hs_find_upd` first normalizes the caller's key: row-store passes a `WT_ITEM`, column-store recnos are packed into a temporary item. Checkpoint reads with no HS checkpoint and readonly disaggregated btrees without a matching shared HS checkpoint return a miss. Otherwise, it opens an HS cursor for `btree->id`, chooses a read timestamp from the checkpoint read timestamp or transaction read timestamp, maps `WT_TS_NONE` to `WT_TS_MAX`, and searches backward before that timestamp. On a hit, it reads stop durable timestamp, durable timestamp, update type, and value.

If the HS update is a reverse modify, `__wt_hs_find_upd` sets `WT_CURSTD_HS_READ_COMMITTED`, walks forward through older HS entries until it finds a standard base value or falls back to the datastore base value, then applies modify records in reverse-pop order through `__wt_modify_apply_item`. Callers can set `upd_value->skip_buf` to check existence without reconstructing the value.

`__wt_hs_btree_truncate` positions a start cursor at the first key for `btree_id`, positions a stop cursor at the first key for `btree_id + 1`, steps back to the last key for the target id, and truncates the inclusive range.

## State And Persistence Behavior
This file directly changes persisted HS content through `__wt_hs_modify` and range truncation. Reads build transient `WT_UPDATE_VALUE` state: `buf`, `tw.durable_start_ts`, `tw.start_txn = WT_TXN_NONE`, and `type`. Modify reconstruction uses temporary scratch buffers and a `WT_UPDATE_VECTOR` to avoid exposing partial state. HS records no longer contain tombstones, and the code asserts that invariant.

## Dependencies And Integration Points
The code depends on HS cursor helpers, btree ids, transaction timestamps, checkpoint metadata, row/column key packing, update allocation, modify application, scratch buffers, and session cursor truncation. It integrates with the read path that restores historical updates, reconciliation/RTS paths that write HS records, and metadata/disaggregated checkpoint selection.

## Risks
The timestamp ordering and search direction are subtle because HS keys include timestamp and counter. Mapping no-timestamp reads to `WT_TS_MAX` prevents hiding newer records. Reverse-modify reconstruction is risky if the base datastore value does not match the expected chain, if `skip_buf` leaks across calls, or if cursor visibility flags are wrong. Truncation relies on HS key ordering by btree id; an incorrect stop cursor could delete another tree's history.

## Test Signals
Tests should cover row and column keys, no-timestamp reads, checkpoint reads with and without HS checkpoints, disaggregated readonly stable handles, standard and modify HS updates, fallback to datastore base values, `skip_buf`, truncating empty and non-empty btree ranges, diagnostic checks for stop cursor positioning, and resource cleanup on all error paths.
