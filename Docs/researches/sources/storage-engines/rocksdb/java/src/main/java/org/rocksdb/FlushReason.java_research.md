# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FlushReason.java

Purpose: enum for reasons RocksDB flushed memtables, including shutdown, external ingestion, manual compaction/flush, write-buffer pressure, delete files, auto compaction, error recovery, WAL full, and catch-up after recovery.

Control flow is package-level byte mapping with `getValue()` and `fromValue(byte)` scanning values and throwing on unknown bytes. State is immutable and used by `FlushJobInfo`. Dependencies include native listener payload conversion.

Risks: byte values must track native `FlushReason`, and unknown bytes fail construction of `FlushJobInfo`. Tests should assert every mapping, invalid-byte behavior, and listener events that produce representative reasons.
