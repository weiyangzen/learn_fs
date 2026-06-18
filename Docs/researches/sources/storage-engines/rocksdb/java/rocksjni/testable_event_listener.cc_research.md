<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/testable_event_listener.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/testable_event_listener.cc

Purpose: Native test helper that invokes every event-listener callback with populated RocksDB event structures so Java listener adapters can be tested without orchestrating real DB events.

Important APIs/types/functions: `newTablePropertiesForTest` creates a `TableProperties` object with maxed numeric fields, string fields, and user/readable properties. `Java_org_rocksdb_test_TestableEventListener_invokeAllCallbacks` unwraps a shared `EventListener` and calls flush, table deletion, compaction, table creation, memtable, CF deletion, external ingestion, background error, stall, file IO, notification, and error recovery callbacks.

Control flow: Java passes an event listener shared pointer handle. The helper builds representative C++ event structs (`FlushJobInfo`, `CompactionJobInfo`, `TableFileCreationInfo`, `MemTableInfo`, `ExternalFileIngestionInfo`, `WriteStallInfo`, `FileOperationInfo`, etc.) and invokes each listener method directly.

State and persistence behavior: No DB persistence occurs; all event structures are synthetic in-memory test data. Some callbacks may mutate Java-side test counters or status fields.

Dependencies and integration points: Depends on generated test JNI header, `rocksdb/listener.h`, `rocksdb/status.h`, and `rocksdb/table_properties.h`. It exercises Java event-listener callback conversion code elsewhere.

Risks: It constructs a `shared_ptr<TableProperties>` with a no-op deleter pointing at a stack object for compaction properties; this is safe only within synchronous callback execution. If listener code stores the shared pointer, it becomes dangling. Max integer values intentionally stress conversion but can expose signed truncation.

Test signals: This file is itself a test signal. Java tests should assert every callback is invoked, all converted fields match expected sentinel values, status/subcode conversion works, file timestamps are converted, and no callback stores stack-backed data beyond the call.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/testable_event_listener.cc -->
