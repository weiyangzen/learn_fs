# sources/storage-engines/wiredtiger/src/cursor/cur_ds.c

## Purpose
This file implements WiredTiger wrapper cursors for extension-provided data sources. It translates WiredTiger cursor API calls to an underlying `WT_DATA_SOURCE` cursor while enforcing WiredTiger cursor state, statistics, collator comparison, and cleanup conventions.

## Important APIs, Types, and Functions
The public entry point is `__wt_curds_open`. Local operation wrappers include `__curds_key_set`, `__curds_value_set`, `__curds_cursor_resolve`, `__curds_bound`, `__curds_compare`, `__curds_next`, `__curds_prev`, `__curds_reset`, `__curds_search`, `__curds_search_near`, `__curds_insert`, `__curds_update`, `__curds_remove`, `__curds_reserve`, and `__curds_close`. Important types are `WT_CURSOR_DATA_SOURCE`, `WT_DATA_SOURCE`, `WT_CURSOR`, and optional `WT_COLLATOR`.

## Control Flow and Behavior
Open allocates a wrapper cursor, reads metadata for `key_format` and `value_format`, initializes the wrapper cursor, optionally configures a collator from metadata/app metadata, calls the extension `open_cursor`, and sanitizes the underlying cursor session, queue, recno, key/value, error, and flag fields.

For search/update style operations, wrappers copy the WiredTiger cursor key/value into the source cursor, call the source method, and resolve the result. For next/prev/search/search_near/insert/update/remove/reserve/bound, `__curds_cursor_resolve` copies successful source key/value/recno back into the wrapper, marks key/value internal, clears set flags on `WT_NOTFOUND`, clears internal flags on other errors, and resets the source cursor after failures to simplify extension behavior. Compare requires both cursors to reference the same object, compares recnos directly for record-number cursors, or uses the configured collator/default compare for byte-string keys. Close closes the source cursor, terminates owned collator, frees allocated formats, and closes the wrapper.

## State and Persistence
The wrapper keeps volatile cursor state and mirrors source cursor key/value/recno state. Persistent data is owned by the extension data source. The wrapper does not implement independent persistence.

## Dependencies and Integration Points
The file depends on metadata lookup, config parsing, collator configuration, cursor API/update/remove macros, system overload checks, statistics macros, extension `WT_DATA_SOURCE` methods, and standard cursor initialization/close helpers.

## Risks
Risks include extension cursors returning pointers with insufficient lifetime, source cursors retaining application memory after key/value assignment, wrapper/source flag divergence, reset-on-error side effects, collator ownership mistakes, and extensions not implementing methods assumed by the method table.

## Test Signals
Signals include extension data-source cursor CRUD behavior, custom collator comparison, append inserts, bound propagation, reset after errors, statistics increments, close cleanup with owned collator, unsupported modify behavior, and metadata-derived format correctness.
