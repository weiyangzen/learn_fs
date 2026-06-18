# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TickerType.java

## Purpose
`TickerType` is the large Java enum mapping RocksDB native ticker counters into byte identifiers usable through JNI statistics APIs.

## Important APIs and Types
The enum covers counters for block cache, secondary/compressed cache, Bloom filters, persistent/simulated cache, memtable and get hits, compaction key drops, write/read byte counts, iterator activity, WAL activity, write grouping, compaction/flush bytes, compression/decompression, row cache, read amplification, rate limiting, BlobDB, transaction overhead, delete scheduler, error handler, backup, remote compaction, tiered storage, last-level/non-last-level reads and seeks, checksum verification, async read, timestamp filtering, FIFO compactions, prefetch, corruption retry, WBWI ingest, user-defined index load failures, multiscans, read-path tombstone conversion, manifest validation, and `TICKER_ENUM_MAX`.

## Control Flow
Each enum stores a byte value. `getTickerType(byte)` scans all enum values and returns the matching type or throws. `Statistics` and `StatisticsCollector` use `getValue()` to request native counts.

## State and Persistence Behavior
No mutable state exists. Tickers represent in-memory native statistics counters; persistence/export is handled by callers or callbacks.

## Dependencies and Integration Points
It is used by `Statistics.getTickerCount`, `Statistics.getAndResetTickerCount`, and `StatisticsCollector`. The file documents an important compatibility decision: native ticker values are wider than Java signed bytes, so newer mappings use the negative byte range instead of preserving native numeric identity.

## Risks and Test Signals
Tests should verify every byte value is unique, sentinel exclusion in collectors, reverse mapping, and synchronization with native ticker mappings in JNI portal code. The biggest risk is byte-space exhaustion or drift when native adds counters; `TICKER_ENUM_MAX` is not numerically last because compatibility requires stable assigned bytes.
