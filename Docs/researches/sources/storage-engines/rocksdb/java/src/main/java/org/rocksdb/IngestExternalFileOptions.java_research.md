# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/IngestExternalFileOptions.java research

## Purpose

`IngestExternalFileOptions` is a `RocksObject` wrapper for native options consumed by `RocksDB.ingestExternalFile(...)`. It controls how externally produced SST files are copied or moved into a DB, how they interact with snapshots and sequence numbers, and whether ingestion may block on memtable flushes.

## Important APIs and types

The default constructor creates native defaults. The four-argument constructor initializes `moveFiles`, `snapshotConsistency`, `allowGlobalSeqNo`, and `allowBlockingFlush`. Fluent setters and getters cover those fields plus `ingestBehind` and `writeGlobalSeqno`. All public mutators return `this`; all real storage lives behind `nativeHandle_`.

## Control flow

Construction calls `newIngestExternalFileOptions(...)`. Each getter and setter is a direct JNI call. Disposal calls `disposeInternalJni(handle)`. There is no Java-side validation of combinations such as ingest-behind requiring DB-level `allowIngestBehind`.

## State and persistence behavior

Java state is the owned native handle. The options influence persistent DB state during ingestion: files may be moved rather than copied, global sequence numbers can be assigned or written into files for compatibility, snapshots can be protected from newly ingested keys, and ingest-behind places files at the bottommost level with sequence number zero.

## Dependencies and integration points

The class integrates with `RocksDB.ingestExternalFile(ColumnFamilyHandle, List, IngestExternalFileOptions)`, external SST creation flows, DB-level `allowIngestBehind`, snapshots, memtables, and sequence-number assignment in native RocksDB.

## Risks and test signals

The main risks are unsafe option combinations delegated to native code, lifecycle misuse after `close()`, and compatibility surprises around `writeGlobalSeqno`. Tests should cover getter/setter round-trips, default values, ingestion with overlapping key ranges, snapshot visibility, move-vs-copy file behavior, ingest-behind prerequisites, and downgrade-compatible global-seqno writes.
