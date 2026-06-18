# sources/storage-engines/wiredtiger/src/history/hs_conn.c

## Purpose
This file owns history-store lifecycle at connection setup and shutdown. It creates the local history store, optionally creates the shared disaggregated history store, configures the opened history-store btree handles, records the history-store file id in cache state, and clears legacy lookaside storage from upgraded databases.

## Important APIs, Types, And Functions
`__wt_hs_open` is the startup entry point. It opens an internal session, drops `file:WiredTigerLAS.wt` if present, creates `WT_HS_URI`, creates `WT_HS_URI_SHARED` for disaggregated connections, and delegates to `__wt_hs_config`. `__wt_hs_config` iterates history-store ids with `__wt_curhs_next_hs_id` and calls `__hs_config`. `__hs_config` validates `history_store.file_max`, opens a temporary internal session named `hs_access`, retrieves the btree through `__hs_get_btree`, sets `btree->file_max`, updates `cache_hs_ondisk_max`, records `conn->cache->hs_fileid`, and sets `WT_CONN_HS_OPEN`. `__wt_hs_close` clears the open flag. `__hs_cleanup_las` removes the obsolete lookaside file under the schema lock.

## Control Flow
Startup exits early for readonly or in-memory connections because no writable history store is needed. Otherwise, `__wt_hs_open` uses a dedicated internal session so recovery-time default-session concurrency does not corrupt setup. Creation is idempotent at the schema layer and then configuration uses real history-store cursors to get the btree backing each HS id. The configuration loop is open-ended and terminates on `WT_NOTFOUND`, which allows future local/shared ids without hard-coding a fixed count.

## State And Persistence Behavior
This file persists history-store existence by creating the HS table files and, for disaggregated deployments, the shared HS table with `block_manager=disagg`. It does not write HS records directly. Runtime state changes are connection-global: `WT_CONN_HS_OPEN` advertises HS availability, `conn->cache->hs_fileid` identifies the HS file for cache accounting, and each HS btree's `file_max` enforces configured on-disk bounds. Legacy lookaside cleanup is persistent because it drops an old file if an upgraded home still contains it.

## Dependencies And Integration Points
The code depends on schema operations, internal sessions, history-store cursor helpers, cache statistics, connection flags, and configuration parsing. It integrates with `btmem.h` HS URI/config definitions, `btree.h` file id fields, the cache's HS accounting, and disaggregated storage detection. It must run before any component expects `WT_CONN_HS_OPEN` and before reconciliation or reads rely on history-store cursors.

## Risks
Misconfiguring `history_store.file_max` below `WT_HS_FILE_MIN` is rejected. Failing to close temporary sessions can leak internal resources, so all setup paths use cleanup in `err`. Opening cursors to retrieve btree handles during startup is sensitive to partial creation failure. The `WT_CONN_HS_OPEN` flag must only be set after the btree is actually open; otherwise readers could attempt HS access too early.

## Test Signals
Test startup in normal, readonly, in-memory, and disaggregated modes. Exercise upgrades that still have `WiredTigerLAS.wt`, invalid and valid `history_store.file_max`, shared HS creation, file id assignment, shutdown flag clearing, and injected failures during internal session open, schema create/drop, cursor open, and configuration.
