# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/IngestExternalFileOptionsTest.java

## Purpose

Accessor and constructor coverage for `IngestExternalFileOptions`.

## Important APIs, control flow, and dependencies

The tests construct options with no arguments and with constructor booleans, then round-trip `moveFiles`, `snapshotConsistency`, `allowGlobalSeqNo`, `allowBlockingFlush`, `ingestBehind`, and `writeGlobalSeqno`.

## State, persistence, risks, and test signals

No external files are ingested here. These options affect later persisted SST ingestion semantics. Risks include constructor parameter order drift, default value changes, and boolean JNI binding errors. Signals are exact getter equality and known false defaults for `ingestBehind` and `writeGlobalSeqno`.
