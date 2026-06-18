# sources/storage-engines/wiredtiger/src/btree/bt_cursor.c

## Purpose
Provides the core btree cursor operations above page traversal: search, search-near, insert, update, modify, reserve, remove, truncate, compare/equal, cursor reset/open/close, bounds positioning, validity checks, conflict checks, state save/restore, and optional eviction/reposition behavior.

## Important APIs, types, and functions
- `WT_CURFILE_STATE` stores external key/value/recno/flags so failed operations can restore cursor state.
- Search APIs: `__wt_btcur_search`, `__wt_btcur_search_near`, `__wt_btcur_search_prepared`.
- Mutation APIs: `__wt_btcur_insert`, `__wt_btcur_insert_check`, `__wt_btcur_remove`, `__wt_btcur_update`, `__wt_btcur_modify`, `__wt_btcur_reserve`.
- Range/compare APIs: `__wt_btcur_compare`, `__wt_btcur_equals`, `__wt_cursor_truncate`, `__wt_btcur_range_truncate`.
- Lifecycle APIs: `__wt_btcur_init`, `__wt_btcur_open`, `__wt_btcur_reset`, `__wt_btcur_close`, `__wt_btcur_free_cached_memory`.
- Helper families include bounds checks/positioning, valid-row/valid-column checks, search dispatch, modify dispatch, update-conflict checks, modify-chain full-update decisions, and evict-reposition.

## Control flow
Search localizes any pinned key, clears pinned values, checks bounds, optionally searches the pinned page, searches from the root when needed, validates visibility, returns key/value or key-only data, initializes diagnostic key-order state, and restores external state on failure. Search-near may reposition an out-of-bounds search key to the nearest bound, tries a row pinned-page optimization, searches from root, and if no valid exact record exists walks next then prev to find a neighbor.

Insert validates key/value sizes, disables bulk load, handles append-key allocation for column store, checks bounds, tries a pinned-page overwrite fast path, otherwise searches and either rejects duplicates or calls row/column modify. Remove and update share the pattern of pinned-page fast path, search with restart handling, conflict checking before visibility decisions, mutation through `__cursor_modify`, and state restoration on errors. Modify requires explicit snapshot transactions, materializes the current value, packs and applies modify entries, chooses a delta or full update based on value size and update-chain shape, and delegates to update. Reserve temporarily sets overwrite behavior and writes a reserve update.

Truncate logs the range when needed, then repeatedly searches/positions the start cursor, removes current records with the supplied remove function, advances with `next` in truncate mode, and stops at the end cursor or end of tree.

## State and persistence behavior
This file does not write blocks directly; persistence is through row/column modify calls that append updates/tombstones/reserve/modify records to page update chains. It carefully manages cursor external versus internal key/value flags, pinned pages, update values, retry state, overwrite/append flags, and transaction conflict checks. Truncate logs logical start/stop keys for recovery while in-memory updates are still tracked for rollback. Modify operations may persist compact delta updates or full values depending on chain state.

## Dependencies and integration points
The file integrates with row/column search and modify implementations, transaction visibility/conflict/autocommit code, history-store reads, cursor bounds comparison, next/prev traversal, eviction and hazard reset, btree bulk-load state, update-chain structures, truncate logging, collators, LSM insert-check behavior, prepared transaction resolution, and diagnostic format-test callbacks.

## Risks and edge cases
- Error paths must restore external cursor state while releasing pinned pages; `WT_CURFILE_STATE` correctness is central.
- Conflict checks must occur before visibility checks for remove/update or write conflicts can be missed.
- Pinned-page fast paths are disabled in several cases, including read-committed search and forced eviction, to avoid inconsistent results.
- Modify is restricted to explicit snapshot transactions because it relies on a stable current value.
- Bounds logic can reposition search-near and unpositioned next/prev; inclusive/exclusive bound handling has subtle exact-value cases.
- Truncate uses cursor positional equality for row-store fast paths, so cursors must be fully instantiated.

## Test signals
Tests should cover search/search-near with and without pinned pages, bounds inclusive/exclusive behavior, append inserts, overwrite and no-overwrite duplicate handling, update/remove conflict detection, prepared update resolution, reserve updates, modify in snapshot versus unsupported isolation/autocommit modes, modify-chain full-update thresholds, compare/equal for row and column stores, range truncate with logging and rollback, evict-reposition under snapshot isolation, and cursor close/free/reset memory behavior.
