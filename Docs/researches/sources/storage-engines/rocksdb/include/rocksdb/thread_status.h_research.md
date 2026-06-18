# Research: sources/storage-engines/rocksdb/include/rocksdb/thread_status.h

- **Purpose:** Exposes runtime status snapshots for RocksDB-related threads returned by `GetThreadList()`.
- **Important APIs/types/functions:** `ThreadStatus` includes `ThreadType`, `OperationType`, `OperationStage`, compaction/flush property enums, `StateType`, immutable fields such as thread id, DB/CF names, operation, elapsed micros, stage, state, and `op_properties`. Utility methods translate enum values and elapsed times to human-readable strings.
- **Control flow:** Instrumented RocksDB threads update internal status tracking while running operations such as compaction, flush, DB open, Get/MultiGet, iterator, checksum verification, and manifest file checksum retrieval. `GetThreadList()` copies those states into public `ThreadStatus` objects.
- **State and persistence:** Status is transient diagnostic state. `kEnabled` tells callers whether RocksDB was built with thread-status support. Operation properties are positional and change meaning by operation type.
- **Dependencies:** Depends on standard containers and the RocksDB namespace. DB APIs populate the structure from internal thread-local/global tracking.
- **Integration points:** Admin tools, logs, and tests use the translation helpers to display currently running compactions, flushes, and read operations.
- **Risks:** The header still documents the feature as under development, so enum and class definitions can change. Misinterpreting `op_properties` without operation-specific names yields incorrect diagnostics.
- **Test signals:** Tests should cover build-enabled/disabled behavior, enum-name mapping, stage transitions during flush/compaction, elapsed-time formatting, and property-name lookup bounds.
