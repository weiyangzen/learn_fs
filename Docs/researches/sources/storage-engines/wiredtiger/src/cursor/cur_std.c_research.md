# sources/storage-engines/wiredtiger/src/cursor/cur_std.c

## Purpose
Provides shared cursor infrastructure: default unsupported/no-op handlers, key/value packing and unpacking, raw helpers, cursor modify fallback, cursor caching/reopen, runtime reconfiguration, bounds management, position duplication, generic initialization, close, equality, and diagnostic dispatch.

## Important APIs, types, and functions
Default methods include `__wti_cursor_noop`, `__wt_cursor_notsup`, `__wti_cursor_*_notsup`, and `__wti_cursor_set_notsup`. Key/value helpers are `__wti_cursor_get_keyv`, `__wti_cursor_set_keyv`, `__wti_cursor_get_valuev`, `__wti_cursor_set_valuev`, `__wt_cursor_get_raw_key`, `__wt_cursor_set_raw_key`, `__wt_cursor_get_raw_value`, `__wt_cursor_set_raw_value`, and `__wt_cursor_get_raw_key_value`. Cache functions are `__wti_cursor_cache`, `__wti_cursor_reopen`, `__wti_cursor_cache_release`, `__wti_cursors_can_be_cached`, and `__wt_cursor_cache_get`. Other central APIs are `__wti_cursor_reconfigure`, `__wti_cursor_bound`, `__wt_cursor_bounds_save`, `__wt_cursor_bounds_restore`, `__wt_cursor_dup_position`, `__wt_cursor_init`, `__wt_cursor_close`, and `__wt_cursor_equals`.

## Control flow
Get/set helpers wrap standard API accounting, validate key/value flags, and fast-path common formats (`u`, `S`, record numbers, and byte formats) while falling back to WiredTiger struct pack/unpack. Setters release debug-copy buffers, preserve/reuse allocated `WT_ITEM` storage when possible, and record `saved_err` on failure. Cursor close either destroys or, via caller paths, may cache eligible cursors. Cache release resets the cursor, clears bounds, preserves useful buffers, acquires/releases dhandle references, moves the cursor between session open and cache queues, and adjusts statistics. Cache get matches by URI hash and URI, reopens the cursor, repairs flag-only configuration differences, and restores btree read-once/dhandle side effects.

## State, persistence, and dependencies
The file owns no durable data but manages long-lived cursor memory, session cursor queues, cursor flags, bounds buffers, URI hashes, open/cached cursor counts, and dhandle use counts. It depends on config parsing, WiredTiger struct packing, session/dhandle sweep, dump cursor wrapping, transaction isolation for modify, compare/collator helpers, statistics macros, and diagnostic btree/layered debug hooks.

## Integration points
Nearly every cursor type uses these helpers either directly through `WT_CURSOR_STATIC_INIT` method tables or indirectly through `__wt_cursor_init`. Table, metadata, statistics, history/version, btree, dump, and layered cursors rely on this file for consistent API behavior, read-only enforcement, cacheability rules, bounds semantics, and error messages.

## Risks and test signals
This is high-blast-radius code. Risks include dangling application-memory references after set/get, incorrect key/value flag transitions, cached cursor reuse with incompatible config, dhandle lifetime leaks, bounds restore failures across composed cursors, and modify running outside supported transaction isolation. Tests should cover all key/value formats including raw mode, cursor-copy debug, append/overwrite/read-only config, dump wrappers, cache hit/miss/reopen/sweep paths, bounds overlap/equality/inclusive rules, cursor duplication, and fallback modify in explicit snapshot transactions.
