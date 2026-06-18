# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/EventListener.java

Purpose: callback interface for RocksDB events, enabling Java code to observe flushes, compactions, file IO, table-file lifecycle, memtable changes, write stalls, error recovery, and external file ingestion.

Control flow is callback-driven from native RocksDB through listener wrappers. The interface documentation is a major behavioral contract: callbacks run on the actual RocksDB event thread, without DB mutexes held, and should return quickly; long DB operations should be offloaded to another thread. Callback arguments are either copied Java value objects or native-backed structs depending on event type. State is implementation-defined in user listeners; RocksDB stores listener registrations through options.

Dependencies include `RocksDB`, `FlushJobInfo`, `CompactionJobInfo`, `FileOperationInfo`, `TableFileCreationInfo`, `TableFileDeletionInfo`, `MemTableInfo`, `WriteStallInfo`, `ExternalFileIngestionInfo`, and error-recovery payload types.

Risks: blocking callbacks can stall flush/compaction/write paths, borrowed native objects may have limited lifetime, and listener exceptions crossing JNI need careful handling. Tests should register listeners, verify callback ordering/payloads, ensure no DB mutex deadlock for safe offloaded operations, and cover listener retention in `DBOptions`.
