# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HistogramType.java

Purpose: enum of RocksDB histogram metric identifiers for DB operations, compaction, IO, blob DB, flush, multiget/multiscan, async IO, ingestion, and related timing/size distributions.

Control flow maps each histogram to an explicit byte, exposes `getValue()`, and provides `getHistogramType(byte)` with invalid-byte exception. State is immutable and consumed by `Statistics` APIs to select a histogram. Dependencies include `Statistics`, `HistogramData`, and native ticker/histogram definitions.

Risks: byte values are extensive and sparse (`0x3E` reserved/max, `0x3F` used after it), making ordinal assumptions unsafe; new native metrics require Java updates. Tests should verify all byte mappings, invalid-byte behavior, selected statistics lookups, and compatibility when native exposes unknown metrics.
