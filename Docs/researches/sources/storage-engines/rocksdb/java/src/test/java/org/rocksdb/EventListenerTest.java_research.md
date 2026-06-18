# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/EventListenerTest.java

## Purpose

Tests Java `AbstractEventListener` callback delivery, callback metadata conversion, enabled-callback filtering, and real DB operations that trigger flush, compaction, file deletion, handle deletion, and external ingestion events.

## Important APIs, control flow, and dependencies

The helper flows open temporary DBs with listeners. `flushDb` writes and flushes to trigger `onFlushBegin`, `onFlushCompleted`, table creation, and memtable events. `deleteTableFile` writes enough data, flushes, compacts, then `deleteFilesInRanges` to trigger table deletion. `compactRange` triggers compaction begin/completed. `deleteColumnFamilyHandle` closes a handle to trigger deletion-started. `ingestExternalFile` writes an SST via `SstFileWriter` and calls `ingestExternalFile`.

The synthetic callback test builds `TableProperties`, `FlushJobInfo`, `Status`, table/file/memtable/write-stall/external-ingestion info objects, and a `CapturingTestableEventListener` to invoke every callback and assert payload equality.

## State, persistence, risks, and test signals

Real tests persist memtables to SSTs, compact files, delete ranges, and ingest external files. Callback state may be written from native background threads, so `ListenerEvents` fields are volatile. Risks include listener lifetime, callback thread visibility, platform-specific file IO events, stale metadata conversion, and callback filtering errors. Signals are atomic booleans from real callbacks, full event coverage from synthetic invocation, enabled-event filtering, and captured assertion propagation.
