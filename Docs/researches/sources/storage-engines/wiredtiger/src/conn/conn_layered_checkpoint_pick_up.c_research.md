# sources/storage-engines/wiredtiger/src/conn/conn_layered_checkpoint_pick_up.c

## Purpose
This file implements follower checkpoint pickup for disaggregated storage. It parses checkpoint metadata supplied through configuration, fetches shared metadata from the page log, updates the local metadata table with the picked-up shared metadata checkpoint, reconciles local and shared table/file metadata, creates missing ingest tables, invalidates stale handles, updates checkpoint bookkeeping, and validates checkpoint metadata versions.

## Important APIs, Types, and Functions
`__wti_disagg_pick_up_checkpoint_meta` is the external entry point. It copies the metadata config string, parses `metadata_lsn`, optional `metadata_checksum`, `database_size`, `version`, and `compatible_version`, opens an internal `checkpoint-pick-up` session, and calls `__disagg_pick_up_checkpoint` under the checkpoint lock.

`__disagg_pick_up_checkpoint` rejects older metadata LSNs, warns and exits for duplicate LSNs, fetches the shared metadata page with `__wti_disagg_fetch_shared_meta`, parses it with `__wt_disagg_parse_meta`, loads crypt key metadata if configured, updates the local metadata entry for `WT_DISAGG_METADATA_URI`, applies per-table metadata through `__disagg_apply_checkpoint_meta`, prunes the local shared-metadata operation queue, finalizes checkpoint state, and updates success/failure stats.

`__disagg_apply_checkpoint_meta` is the main reconciliation loop. It opens local metadata cursors and checkpoint cursors on the shared metadata table for `colgroup:`, `file:`, `layered:`, and `table:` prefixes. It advances all cursors in sorted logical table-name order, compares local/shared presence for each URI scheme, inserts new metadata, updates existing file checkpoint metadata, creates missing ingest tables from layered config, and handles local-only or dropped-table cases.

Helper functions include `__disagg_save_checkpoint_meta_local`, `__disagg_update_file_meta`, `__disagg_insert_meta`, `__disagg_bound_cursor`, `__disagg_table_name`, `__disagg_file_skip_local`, `__disagg_discard_old_checkpoint_check`, `__layered_create_missing_ingest_table`, `__raise_next_file_id`, and `__disagg_finalize_checkpoint_meta`.

## Control Flow and Behavior
The pickup entry point first turns a bounded config slice into a null-terminated string. It treats missing checksum as a backward-compatible warning, validates metadata version compatibility, then uses an internal session and checkpoint lock so pickup cannot race checkpoint begin/advance or role transition.

Pickup first checks LSN monotonicity against `last_checkpoint_meta_lsn`. It then fetches and parses the shared metadata root. The local shared metadata table entry is updated by collapsing the new `checkpoint=` config into its local metadata record. If the checkpoint changed, any old checkpoint handle for the shared metadata table is marked outdated.

The metadata apply loop opens four local and four shared cursors, bounds each by URI scheme, and processes all metadata for one logical table name at a time. Existing layered tables get their stable `file:` checkpoint metadata updated or inserted. New layered tables are ignored if the local metadata queue says the latest local create/remove operation is `REMOVE`; otherwise the code creates the ingest table if referenced and absent, then inserts layered, file, colgroup, and table entries from shared metadata. Non-layered shared table, colgroup, and file entries are inserted or updated where supported. Local metadata entries without shared counterparts are currently logged but mostly left in place.

Finalization stores the new checkpoint metadata LSN, schema epoch, checkpoint timestamp, oldest timestamp, transaction-global checkpoint timestamp fields, database size, last checkpoint root string, updates ingest prune timestamps, and raises `next_file_id` if needed.

## State and Persistence Behavior
The persistent effects are local metadata table updates and optional creation of missing ingest tables. Local metadata's `checkpoint=` fields for stable/shared files are overwritten with checkpoint information from the shared metadata checkpoint, while other metadata fields are preserved through config collapse. Old checkpoint dhandles are marked outdated so future opens use the new metadata.

In-memory state updated during finalization includes checkpoint metadata LSN, schema epoch, checkpoint timestamps, database size, last checkpoint root, transaction-global last checkpoint timestamp, and file id allocator. The code also prunes the connection's pending shared metadata queue up to the picked-up schema epoch, because those operations are now represented in shared metadata.

## Dependencies and Integration Points
This file depends on PALI/page-log metadata fetch and parse helpers, local and shared metadata cursors, layered table schema config, dhandle invalidation, schema locks, checkpoint locks, key provider loading, ingest prune logic from `conn_layered_ingest.c`, and shared metadata queue inspection from `conn_layered.c`.

It integrates with `__wti_disagg_conn_config` during startup and follower reconfigure, model/cppsuite helpers that call `reconfigure(disaggregated=(checkpoint_meta=...))`, and tests for layered follower pickup and failover.

## Risks
The four-way cursor merge is correctness-critical. Table names are derived differently for `file:` keys by stripping `.wt` and `.wt_stable`, and local ingest files are skipped so they are not mistaken for shared stable files. Bugs in name normalization or cursor advancement can pair metadata entries from different tables or miss a URI scheme.

The code updates only checkpoint information for existing file metadata and has FIXME notes about verifying all other metadata fields. If leader and follower metadata diverge outside checkpoint config, pickup may not detect it. Dropped local layered tables are not fully removed yet. Creating missing ingest tables from shared layered config depends on key/value format extraction and schema create under the schema lock.

Older checkpoint pickup is rejected, duplicate pickup is a no-op, and incompatible metadata versions return `ENOTSUP`. These guards protect followers from rolling back state or reading a newer checkpoint format incorrectly.

## Test Signals
Signals include `layered_table_manager_checkpoints_disagg_pick_up_succeed`, follower pickup count, failure count, `disagg_apply_checkpoint_meta_time`, inserted/updated file metadata stats, updated database size, last checkpoint timestamps, and stale dhandle invalidation. Tests should cover new layered table pickup, existing table checkpoint update, shared history store file-only entries, dropped table races, duplicate and older metadata LSN handling, missing checksum backward compatibility, incompatible version rejection, and missing shared file metadata errors.
