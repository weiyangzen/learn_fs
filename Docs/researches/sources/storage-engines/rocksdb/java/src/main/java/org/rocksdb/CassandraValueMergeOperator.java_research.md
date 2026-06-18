# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CassandraValueMergeOperator.java

- **Purpose:** Java wrapper for the native Cassandra wide-column value merge operator.
- **Important APIs/types/functions:** Extends `MergeOperator`; constructors accept `gcGracePeriodInSeconds` and optional `operandsLimit`; native `newSharedCassandraValueMergeOperator` allocates the shared operator; `disposeInternal` calls `disposeInternalJni`.
- **Control flow:** Construction creates a native merge operator with GC grace and operand limit settings. Merge logic runs in C++ during reads/compaction; Java only owns/releases the handle.
- **State and persistence behavior:** Native merge operator affects persisted values produced by merges and compactions. Java has no additional state beyond the native handle.
- **Dependencies:** Depends on `MergeOperator` and Cassandra native merge code.
- **Integration points:** Passed to `ColumnFamilyOptions.setMergeOperator()` for Cassandra-compatible value merging.
- **Risks:** Operand limit and GC grace semantics must match Cassandra value encoding. Native shared operator ownership must be released exactly once.
- **Test signals:** Merge correctness with Cassandra values, operand-limit behavior, GC grace behavior, database reopen/compaction behavior, and close idempotence inherited from native wrapper base.
