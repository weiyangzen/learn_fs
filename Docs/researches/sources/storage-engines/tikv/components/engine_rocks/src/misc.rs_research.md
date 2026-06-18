<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/misc.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/misc.rs

Purpose: implements miscellaneous engine operations: flushing, range deletion strategies, memtable/LSM stats, WAL sync, background work control, DB existence/lock checks, and engine statistics.

Important APIs/types/functions: `MAX_DELETE_COUNT_BY_KEY`, private `delete_all_in_range_cf_by_ingest`, `delete_all_in_range_cf_by_key`, and `MiscExt for RocksEngine`.

Control flow: flush methods resolve CF handles and configure RocksDB `FlushOptions`. Range deletion dispatches by `DeleteStrategy`: delete files, delete Titan blobs, range tombstones, key-by-key deletes, or generated delete SST ingestion. Delete-by-writer collects keys, switches to SST writer after a threshold, then ingests the delete SST with optional range locking.

State and persistence behavior: mutates memtables, WAL, SST files, blob files, range tombstones, and background/manual compaction state. Some deletes sync WAL when required.

Dependencies/integration: relies on iterator, write batch, import, SST writer, RocksDB properties, and metrics modules.

Risks: delete-file/blob strategies can expose old blob indexes if misused; Titan paths require key-only iteration. Background-work pause toggles global manual-compaction state shared by DB instances.

Test signals: tests cover range deletion strategies, delete-file/blob behavior, prefix-bloom delete range case, and oldest-memtable flush selection.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/misc.rs -->
