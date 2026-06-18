<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/cassandra_value_operator.cc -->
# Research: sources/storage-engines/rocksdb/java/rocksjni/cassandra_value_operator.cc

Purpose: Implements JNI bindings for Java `CassandraValueMergeOperator`, creating and disposing a shared C++ Cassandra merge operator.

Important APIs/types/functions: `Java_org_rocksdb_CassandraValueMergeOperator_newSharedCassandraValueMergeOperator` allocates a `std::shared_ptr<MergeOperator>` wrapping `cassandra::CassandraValueMergeOperator`; `disposeInternalJni` deletes the shared pointer wrapper.

Control flow: The factory converts Java `gcGracePeriodInSeconds` and `operands_limit` to the C++ constructor, returns the heap-allocated shared-pointer handle, and disposal reinterprets/deletes that handle.

State and persistence behavior: The merge operator is native process state referenced by DB options. It affects persisted values when merge operands are resolved or compacted under Cassandra value semantics, including garbage-collection grace and operand limits.

Dependencies and integration points: Depends on generated JNI headers, RocksDB DB/options/merge operator headers, Cassandra merge utilities, and Java merge-operator wrapper ownership.

Risks and edge cases: The Java options object must keep the shared operator alive for as long as the DB uses it. Misconfigured operand limits or grace periods can affect merge correctness and compaction output. Disposed handles must not be reused.

Test signals: Java merge-operator tests should exercise construction, DB option installation, merge/read/compaction outcomes, operand-limit behavior, and native disposal under JNI checking.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/cassandra_value_operator.cc -->
