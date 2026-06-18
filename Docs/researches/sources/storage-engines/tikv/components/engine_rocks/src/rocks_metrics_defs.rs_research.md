<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/rocks_metrics_defs.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/rocks_metrics_defs.rs

## Purpose
`rocks_metrics_defs.rs` centralizes string constants for RocksDB/Titan DB properties and the ticker/histogram type lists that `rocks_metrics.rs` flushes. It is the compatibility table between RocksDB property names and TiKV metric collection code.

## Important APIs, Types, and Functions
The file exports property-name constants such as `ROCKSDB_TOTAL_SST_FILES_SIZE`, `ROCKSDB_CUR_SIZE_ALL_MEM_TABLES`, `ROCKSDB_ESTIMATE_NUM_KEYS`, `ROCKSDB_NUM_FILES_AT_LEVEL`, and Titan property names for blob counts, live/obsolete sizes, and discardable-ratio buckets. `ROCKSDB_IOSTALL_KEY` and `ROCKSDB_IOSTALL_TYPE` map RocksDB cfstats keys to TiKV metric labels.

`ENGINE_TICKER_TYPES`, `TITAN_ENGINE_TICKER_TYPES`, `ENGINE_HIST_TYPES`, and `TITAN_ENGINE_HIST_TYPES` define the exact RocksDB statistics variants drained or observed by the metrics flusher.

## Control Flow
There is no runtime control flow. Consumers iterate the exported arrays and pass each enum value to `RocksStatistics`. Property helpers concatenate level suffixes to prefix constants such as `ROCKSDB_COMPRESSION_RATIO_AT_LEVEL`, `ROCKSDB_NUM_FILES_AT_LEVEL`, and `ROCKSDB_TITANDB_NUM_BLOB_FILES_AT_LEVEL`.

## State and Persistence Behavior
The module is immutable definitions only. Its choices affect which RocksDB counters are reset during metrics flushes and which DB properties are interpreted.

## Dependencies and Integration Points
It imports RocksDB `DBStatisticsTickerType` and `DBStatisticsHistogramType`. `rocks_metrics.rs` and `util.rs` are the main consumers. Any change to metric dispatch needs to keep these arrays and the match arms in sync.

## Risks and Edge Cases
Property strings are version-sensitive and typo-sensitive. Adding an enum to an array without adding a match arm produces no metric for that value if the flusher falls through. `TITAN_ENGINE_TICKER_TYPES` contains repeated Titan GC action variants, so duplicate draining can reset/report zero on later occurrences depending on RocksDB counter behavior.

## Test Signals
The `rocks_metrics.rs` flush test iterates these arrays. Stronger coverage would assert that every listed ticker/histogram has a non-ignored mapping unless intentionally documented.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/rocks_metrics_defs.rs -->
