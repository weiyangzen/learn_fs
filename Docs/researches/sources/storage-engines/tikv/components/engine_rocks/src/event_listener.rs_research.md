<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/event_listener.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/event_listener.rs

Purpose: implements RocksDB event listeners for metrics, IO-type attribution, background-error handling, SST recovery scheduling, and persistence progress callbacks.

Important APIs/types/functions: `RocksEventListener`, `resolve_sst_filename_from_err`, `RocksPersistenceListener`, and `rocksdb::EventListener` callbacks for flush, compaction, ingestion, background errors, stalls, memtable seal, and flush completion.

Control flow: begin callbacks tag current IO type; completion callbacks increment metrics and reset IO type. Background errors ignore recoverable no-space flush/compaction errors, optionally schedule SST recovery for corruption/IO errors, reset status on accepted recovery, or panic after setting corruption panic marks. Persistence callbacks convert memtable/flush metadata into `PersistenceListener` events.

State and persistence behavior: mutates global metrics, IO-type thread state, critical-error counters, panic marks, and external persistence progress storage.

Dependencies/integration: hooks into RocksDB option event listeners, TiKV scheduler, file-system IO limiter, and raftstore persistence tracking.

Risks: SST filename regex only captures a slash plus word `.sst`, so unusual paths may not recover. Background panic policy is intentionally severe.

Test signals: tests cover SST filename extraction and persistence listener sequencing across flushes and merged memtables.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/event_listener.rs -->
