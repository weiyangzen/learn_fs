<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/cassandra_compactionfilterjni.cc -->
# Research: sources/storage-engines/rocksdb/java/rocksjni/cassandra_compactionfilterjni.cc

Purpose: Implements the JNI factory for Java `CassandraCompactionFilter`, creating the C++ Cassandra compaction filter used by RocksDB's Cassandra-format utilities.

Important APIs/types/functions: `Java_org_rocksdb_CassandraCompactionFilter_createNewCassandraCompactionFilter0` allocates `cassandra::CassandraCompactionFilter` with `purge_ttl_on_expiration` and `gc_grace_period_in_seconds`, then returns the native pointer.

Control flow: The factory receives Java boolean/int parameters, constructs the C++ filter with those values, and returns the pointer using `GET_CPLUSPLUS_POINTER`.

State and persistence behavior: The returned compaction filter object is native heap state owned through the Java wrapper. It affects future compaction output by purging/retaining expired Cassandra cells according to TTL and grace-period policy.

Dependencies and integration points: Depends on generated JNI headers, `utilities/cassandra/cassandra_compaction_filter.h`, and JNI pointer conversion helpers. It integrates with Java `CassandraCompactionFilter` and RocksDB compaction configuration.

Risks and edge cases: Ownership and disposal must be handled by the Java base filter wrapper; this file only allocates. Incorrect TTL/grace settings can change persisted data during compaction.

Test signals: Java compaction-filter tests should verify native handle creation, disposal, and compaction behavior for expired/non-expired Cassandra values.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/cassandra_compactionfilterjni.cc -->
