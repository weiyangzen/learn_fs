# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CassandraCompactionFilter.java

- **Purpose:** Thin Java wrapper around RocksDB's native Cassandra compaction filter.
- **Important APIs/types/functions:** Extends `AbstractCompactionFilter<Slice>`. Constructor accepts `purgeTtlOnExpiration` and `gcGracePeriodInSeconds`, then calls native `createNewCassandraCompactionFilter0`.
- **Control flow:** Construction creates the native filter; filtering behavior is implemented entirely in C++.
- **State and persistence behavior:** Native filter state/config influences compaction output by purging Cassandra TTL/tombstone data. Java stores no extra fields.
- **Dependencies:** Depends on `AbstractCompactionFilter`, `Slice`, and the Cassandra native utility implementation.
- **Integration points:** Installed with `ColumnFamilyOptions.setCompactionFilter()` for Cassandra-format value compaction.
- **Risks:** Correctness depends on native Cassandra value encoding and TTL semantics. The filter object must stay alive as long as options/DB can use it.
- **Test signals:** Compaction behavior with Cassandra values, TTL expiration/purge behavior, gc grace period handling, and filter disposal after DB close.
