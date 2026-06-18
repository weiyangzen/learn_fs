# sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_open.c

## Purpose
Handles lifecycle and statistics for `WT_BLOCK_DISAGG` handles. It creates no physical file, opens or reuses page-log backed block handles from the connection block hash, closes and destroys those handles, and derives live block size/statistics from checkpoint metadata.

## Important APIs, types, and functions
- `__wt_block_disagg_manager_create` is the create hook and is currently a no-op because remote storage materializes on first access.
- `__wti_block_disagg_open` creates/reuses `WT_BLOCK_DISAGG`, stores table ID, opens the page-log handle, and inserts into the connection block hash.
- `__wti_block_disagg_close` decrements the block refcount under `block_lock` and destroys when it reaches zero.
- `__block_disagg_destroy` removes the block from the connection hash, frees its name, closes `plhandle`, and frees memory.
- `__wt_block_disagg_ckpt_size`, `__wti_block_disagg_stat`, and `__wti_block_disagg_manager_size` expose checkpoint-derived size information.

## Control flow
Create returns success without touching the storage source. Open hashes the filename, checks the connection block hash under `block_lock`, increments `ref` on a match, otherwise allocates a `WT_BLOCK_DISAGG`, inserts it into the hash early for cleanup safety, duplicates the name, marks history-store shared blocks, copies the btree table ID, and opens a page-log handle with `S2BT(session)->page_log->pl_open_handle`. Close locks the block hash, decrements the reference count, and calls destroy when the handle is no longer referenced.

Size/stat calls search the metadata for the file URI, read the most recent checkpoint size with `__wt_ckpt_last_size`, tolerate missing metadata as zero, and write block stats from that value because no local file length exists.

## State and persistence behavior
The connection block hash caches live `WT_BLOCK_DISAGG` handles keyed by filename. Each handle stores `name`, `ref`, `tableid`, optional history-store flag, and page-log handle. Persistent size is not in a filesystem stat; it is the last checkpoint size in the metadata entry. Opening a handle is tied to btree table ID and page-log provider state.

## Dependencies and integration points
This file depends on connection `block_lock`/`blockhash`, page-log provider open/close methods, metadata search and checkpoint config parsing, btree table IDs, history-store naming, and WT statistics. It is called by the manager facade in `block_disagg_mgr.c`.

## Risks and edge cases
- The block is inserted into the hash before all initialization succeeds; cleanup relies on the partially initialized object being destroyable.
- The open loop has a TODO to confirm the found block is the right block type, so name collisions across block-manager kinds would be dangerous.
- Page-log handle creation is asserted as mandatory; disaggregated tables cannot proceed without it.
- Metadata-not-found size returns zero, which is useful for create/open races but can mask missing metadata in diagnostics.
- Reference counting is protected by `block_lock`; any future direct manipulation must preserve that discipline.

## Test signals
Useful tests include create without local files, duplicate opens incrementing refcounts, close destroying only after the last ref, page-log close error propagation, history-store flagging for `WT_HS_FILE_SHARED`, metadata checkpoint-size reads, missing metadata size zero, and stats/manager size reporting.
