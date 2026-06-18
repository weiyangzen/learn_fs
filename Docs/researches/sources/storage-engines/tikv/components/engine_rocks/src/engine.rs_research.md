<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/engine.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/engine.rs

Purpose: implements the core `KvEngine`, `Iterable`, `Peekable`, and `SyncMutable` traits for a RocksDB-backed TiKV engine.

Important APIs/types/functions: `RocksEngine`, `new`, `as_inner`, `get_sync_db`, `support_multi_batch_write`, optional tablet lifetime tracing, and trait methods for snapshot, WAL sync, iterator creation, get, put, delete, and delete range.

Control flow: construction wraps `rocksdb::DB` in `Arc`, records multi-batch support, optionally registers trace lifetime data, and creates an ingest `RangeLatch`. Reads convert engine options to Rocks read options and fetch from default or named CF. Writes resolve CF handles and call RocksDB writable methods.

State and persistence behavior: owns the shared DB handle; snapshots hold point-in-time views; mutations persist through RocksDB WAL/SST mechanisms. `ingest_latch` coordinates ingestion with compaction-filter writes.

Dependencies/integration: central type re-exported by `lib.rs` and extended by many sibling modules.

Risks: `bad_downcast` panics on mismatched types; iterator and CF operations fail at runtime for missing CFs. Trace-lifetime parsing assumes tablet path naming.

Test signals: unit and proptest coverage validates get/put/delete/scan/snapshot behavior and Rocks/Titan equivalence under random operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/engine.rs -->
