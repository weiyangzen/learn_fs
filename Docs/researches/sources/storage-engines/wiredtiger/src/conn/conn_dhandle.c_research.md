# sources/storage-engines/wiredtiger/src/conn/conn_dhandle.c

## Purpose
This file manages connection-level data handles. It allocates and hashes handles for btree, layered, table, tiered, and tiered-tree URIs; loads metadata-backed configuration; opens and closes the underlying objects; marks stale handles outdated; applies callbacks across open btrees; discards handles during close; and refreshes write generations after rollback-to-stable.

## Important APIs, Types, and Functions
`__wt_conn_dhandle_alloc` creates a `WT_DATA_HANDLE` or subtype based on URI prefix (`file:`, `layered:`, `table:`, `tier:`, `tiered:`), initializes locks and names, creates a btree payload for btree handles, and inserts it into both the connection list and hash bucket. `__wt_conn_dhandle_find` searches the hash under the handle-list lock and filters dead/outdated handles, with a special exception for in-use read-only btree checkpoints.

`__conn_dhandle_config_set` reads metadata, builds `dhandle->cfg`, strips checkpoint and live-restore fields into `meta_base` for btree/tiered handles, stores hashes and update timestamps, and chooses defaults for layered/table/tier metadata. `__conn_dhandle_config_parse_ts` sets timestamp assertion and write timestamp usage flags.

`__wt_conn_dhandle_open` reopens a handle with fresh metadata, disables eviction for btrees, initializes dsrc stats on demand, opens the underlying object via btree/schema/tiered helpers, records exclusive ownership, sets `WT_DHANDLE_OPEN`, and increments `open_btree_count` for live handles. `__wt_conn_dhandle_close` performs visibility checks, turns eviction exclusive on/off, flushes or discards data, closes the backing object, marks handles dead when requested, and clears open state.

`__wt_conn_dhandle_close_all`, `__wti_conn_dhandle_discard_single`, and `__wti_conn_dhandle_discard` are schema and connection shutdown paths. `__wt_conn_btree_apply` walks one URI bucket or the full connection handle list and applies a callback to open live btree handles. `__wti_conn_dhandle_outdated` marks matching live handles stale. `__wt_dhandle_update_write_gens` updates btree write generations after rollback-to-stable.

## Control Flow and Behavior
Allocation assumes the caller holds the handle-list write lock and double-checks that no matching handle was inserted by another thread. After type-specific allocation, it initializes the btree payload if needed, metadata flag, rwlock, close lock, name/checkpoint copies, then publishes with a release barrier because sweep may scan without the list lock.

Opening requires an exclusive dhandle unless the caller asked for lock-only. If already open, the handle is closed first so special handles such as verify can use fresh flags. Metadata is reloaded and timestamp flags are parsed. The underlying open is type-specific. For btree and tiered handles, special flags are copied to `WT_BTREE`, dsrc stats are allocated lazily, and eviction exclusive mode is cleared before returning. Metadata open failure with `ENOENT` marks the connection corrupt and returns `WT_ERROR`.

Close first verifies there is no uncommitted data when requested, then excludes eviction and sets advisory eviction flags. It avoids acquiring schema locks while holding an exclusive handle by setting `WT_SESSION_NO_SCHEMA_LOCK` if needed. Under `dhandle->close_lock`, it decides whether to discard, checkpoint-close, or mark dead. Memory-mapped btrees are discarded before closing because mapped pages contain pointers into the mapping; non-mapped discard happens after close. If a handle is merely marked dead, sweep closes it later; otherwise open flags and open count are cleared.

Connection shutdown first closes non-metadata and non-history-store handles because closing dirty user files can write metadata and read history store data. It then closes the history store, clears the session cache, blocks new data-handle use on the default session, closes metadata cursors, and discards remaining handles.

## State and Persistence Behavior
The connection maintains `dhqh` and `dhhash`, reference counts, `session_inuse`, exclusive references, open/dead/outdated/dropped flags, btree write generations, metadata config copies, and per-handle locks. Metadata strings are persisted in the metadata table; this file caches them in `dhandle->cfg`, `meta_base`, `orig_meta_base`, hashes, and timestamps to avoid reparsing checkpoint-heavy fields.

Closing may persist a checkpoint through `__wt_checkpoint_close` unless the tree is non-durable, in-memory, no-checkpoint, dead, or being discarded. Marking a handle outdated does not remove persistence; it prevents future cache hits so new opens load newer metadata. `__wt_dhandle_update_write_gens` updates in-memory generation fields so pages read after rollback-to-stable get transaction IDs reset relative to `conn->base_write_gen`.

## Dependencies and Integration Points
This file is central to session dhandle caches, schema operations, sweep, checkpoint, eviction, metadata, tiered storage, layered tables, history store release, rollback-to-stable, and verbose diagnostics. It uses handle-list locks, handle rwlocks, close locks, metadata tracking, meta-track rollback, btree/tiered/schema open and close helpers, checkpoint close, eviction discard, and transaction visibility.

Disaggregated storage uses `__wti_conn_dhandle_outdated` heavily when checkpoint pickup updates local metadata or role transitions make older stable/read-only handles unsafe.

## Risks
Handle publication and removal are concurrency-sensitive. The release barrier before list insertion protects sweep from partially initialized handles. Close ordering must avoid deadlocks between schema locks, handle locks, and history-store dhandle release. Marking a handle dead before closing the block manager can violate block-manager single-reference assumptions, so the code delays that flag.

Visibility checks are required before closing with uncommitted updates; skipping them can drop or checkpoint unresolved data. Conversely, overly strict checks can make schema operations fail with `EBUSY`. Memory-mapped files have special discard ordering. Outdated read-only checkpoint handles remain findable while in use, which is necessary for disaggregated stable checkpoints but can pin older metadata longer.

## Test Signals
Signals include schema drop/rename/truncate behavior under open cursors, checkpoint handle walking stats, sweep cleanup, rollback-to-stable write generation behavior, metadata corruption on missing metadata handle, and disaggregated checkpoint pickup invalidating old handles. `__wti_verbose_dump_handles` gives runtime diagnostics for reference leaks. Tests should stress close-all with live checkpoint handles, dead/outdated filtering, metadata tracking rollback, and close failures from uncommitted data.
