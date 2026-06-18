# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionReason.java

Purpose: enum describing why RocksDB scheduled a compaction, used mainly by `CompactionJobInfo` and event/listener reporting. It covers level, universal, FIFO, manual, ingestion, TTL, blob GC, temperature, round-robin TTL, and refit-level causes.

Control flow is package-level byte conversion: each enum has an internal byte value, and `fromValue(byte)` scans values or throws. State is immutable and mirrors native event metadata; no Java persistence exists. Dependencies include `CompactionJobInfo` and native listener/job-info code that supplies the byte.

Risks: values are sparse and must align with C++; `kFilesMarkedForCompaction` uses `0x10`, with later reasons around it, so accidental ordinal assumptions are unsafe. Tests should verify every byte mapping, unknown-byte failure, and callback population for representative compaction causes.
