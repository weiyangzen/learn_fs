<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/import.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/import.rs

Purpose: implements external SST ingestion for `RocksEngine`.

Important APIs/types/functions: `ImportExt for RocksEngine`, `ingest_external_file_cf`, `acquire_ingest_latch`, and `RocksIngestExternalFileOptions`.

Control flow: optional ranges acquire `ingest_latch` to serialize with compaction-filter operations when `allow_write` is used. The method resolves the CF, sets move-files and allow-write options, records allow-write metrics, calls optimized RocksDB ingestion, and records blocked/non-blocked duration depending on whether a memtable flush fallback occurred.

State and persistence behavior: moves external SST files into RocksDB, potentially modifies LSM state and WAL-independent data visibility. The latch protects range-local consistency during concurrent writes.

Dependencies/integration: used by snapshot apply, delete-by-writer in `misc.rs`, SST writer builders, and flow-control metrics.

Risks: allow-write ingestion is concurrency-sensitive; incorrect range locking can race compaction-filter writes. Metrics labels contain unusual whitespace in the source string and should be verified by Prometheus users.

Test signals: `test_ingest_multiple_file` builds two external SSTs, forces existing L0 state, and ingests both files successfully.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/import.rs -->
