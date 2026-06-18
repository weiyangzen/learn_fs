# sources/storage-engines/wiredtiger/src/include/cursor_inline.h

## Purpose
`cursor_inline.h` implements hot cursor lifecycle and key/value helper routines shared by multiple cursor `.c` files. It handles cursor activation, reset, key/value ownership, dhandle use counts, table/index value projection, and row-store key fast paths.

## Important APIs, Types, and Functions
`__wt_curhs_get_btree` and `__wt_curhs_get_cbt` unwrap history-store cursors. `__cursor_set_recno`, `__cursor_checkkey`, `__cursor_checkvalue`, `__wt_cursor_localkey`, `__cursor_localvalue`, `__cursor_needkey`, and `__cursor_needvalue` maintain public cursor key/value state. `__cursor_enter`/`__cursor_leave`, `__cursor_reset`, and `__wt_cursor_func_init` implement the main active cursor lifecycle.

Other helpers reset bounds, release debug key/value copies, increment/decrement dhandle session use, return btree key/value pairs, free cached cursor memory, merge projected table/index values, and return row-store slot keys. `__wt_tombstone` plus `__wt_clayered_deleted` encode layered-table deletion markers.

## Control Flow
Before most btree operations, `__wt_cursor_func_init` optionally resets the old position, clears stale insert-stack state, checks cache pressure, activates the cursor, and marks transaction cursor activity. Reset clears position flags, decrements active cursor count, releases read-committed snapshots when no cursors remain, marks delete-heavy pages for eviction/reconciliation, and releases page refs. Key/value helpers copy tree-owned memory into cursor-owned buffers when the application needs stable access across movement.

## State and Persistence Behavior
The helpers mutate cursor flags, buffers, page refs, session active cursor counts, transaction read state, dhandle `session_inuse`, and statistics. They do not directly persist data, but reset can dirty/evict pages to clean obsolete tombstones, and cursor initialization participates in transaction visibility.

## Dependencies and Integration Points
The file depends on eviction, transaction, buffer, schema projection, page release/dirtying, row key unpacking, history-store cursors, layered cursors, and statistics macros. It is included by cursor implementations that need low-overhead access to these shared operations.

## Risks and Edge Cases
Reset ordering is subtle: snapshots are released before page refs because page release can trigger eviction. Dhandle decrement checks `timeofdeath` before subtracting because the handle may be freed afterward. Copy-on-need must correctly distinguish internal page-owned data from cursor-owned buffers. The layered tombstone byte sequence can collide with application values, causing extra copy/check work.

## Test Signals
Cursor reset/close tests, read-committed snapshot release tests, forced eviction/debug reset tests, cursor cache reuse tests, table/index projection tests, prepare-conflict iteration tests, and layered-table deletion tests all exercise this header's behavior.
