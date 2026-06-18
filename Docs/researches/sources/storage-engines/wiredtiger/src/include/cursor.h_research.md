# sources/storage-engines/wiredtiger/src/include/cursor.h

## Purpose
`cursor.h` defines WiredTiger's internal cursor families and cursor state layout. It extends the public `WT_CURSOR` with btree, backup, metadata, table, index, history-store, statistics, version, layered-table, and other specialized cursor implementations.

## Important APIs, Types, and Functions
`CUR2S` maps any cursor to its internal session. `WT_CURSOR_STATIC_INIT` initializes static public cursor vtables. `WT_CURSOR_BTREE` is the main storage cursor, tracking dhandle, current page/ref/slot, insert-list search state, row/column iteration state, cached keys/values, checkpoint transaction metadata, random cursor state, prepare-conflict retry state, and diagnostic key-order fields.

Specialized structs include `WT_CURSOR_BACKUP` for full/incremental backup traversal, `WT_CURSOR_HS` for history-store access, `WT_CURSOR_INDEX` and `WT_CURSOR_TABLE` for schema projection over child cursors, `WT_CURSOR_METADATA`, `WT_CURSOR_STAT`, `WT_CURSOR_VERSION`, and `WT_CURSOR_LAYERED`. Macros identify primary table cursors, recno cursors, raw-output modes, cursor bounds, and positioned btree cursors.

## Control Flow
Public cursor API calls enter through the function pointers embedded in `WT_CURSOR`. Btree cursors search pages and insert lists, cache enough state for next/prev/update/remove, and expose keys/values through buffers owned by the cursor or page. Table/index cursors project values through column-group/index child cursors. Backup and statistics cursors iterate over synthetic lists rather than ordinary btree records. Layered cursors switch between ingest and stable component cursors based on read state.

## State and Persistence Behavior
Cursors are in-memory handles, but they pin durable resources: data handles, pages, checkpoint transactions, history-store checkpoint handles, backup file lists, and incremental backup bitmaps. Cursor flags record API-visible state such as key/value set, bounds, raw mode, active positioning, and cursor-family-specific behavior.

## Dependencies and Integration Points
This header integrates sessions, btrees, pages/refs, insert/update structures, schema tables/indexes, backup metadata, statistics arrays, history store, layered tables, checkpoint transactions, and random utilities. It also relies on generated flag definitions and queue/list conventions.

## Risks and Edge Cases
Cursor state is dense and performance-sensitive. Risks include stale page references after reset, failing to copy page-owned keys before movement, inconsistent active cursor counts, prepare-conflict restart errors, row-store iteration slot mistakes, and bounds checks that do not match positioning state. Backup/incremental cursor flags must stay synchronized with connection backup state.

## Test Signals
Signals include cursor API suites for search/next/prev/update/remove/modify/reserve, bounds tests, raw and dump cursor tests, checkpoint cursor consistency, backup/incremental backup tests, history-store/version cursor tests, random cursor tests, and diagnostic key-order assertions under stress.
