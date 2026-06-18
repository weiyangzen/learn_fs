## `sources/storage-engines/rocksdb/utilities/cassandra/cassandra_compaction_filter.h`

Purpose: declares Cassandra compaction filter and factory types. It documents TTL/tombstone compaction policy and exposes names used by RocksDB object creation.

Important APIs and types: `CassandraCompactionFilter` extends `CompactionFilter`, provides constructor parameters `purge_ttl_on_expiration` and `gc_grace_period_in_seconds`, `kClassName()`, `Name()`, and `FilterV2()`. `CassandraCompactionFilterFactory` extends `CompactionFilterFactory`, stores the same options, implements `CreateCompactionFilter()`, and exposes class name metadata.

Control flow represented by declarations: RocksDB calls the factory per compaction context to obtain a filter. The filter uses `FilterV2()` to decide keep, remove, or change-value for each Cassandra row value.

State and persistence behavior: both classes embed `CassandraOptions`. The filter can rewrite serialized row values or remove keys during compaction; the factory itself is configuration state only.

Dependencies and integration: includes RocksDB compaction filter and slice APIs plus `cassandra_options.h`. Its class names are used by object registry tests and configuration strings.

Risks: comments repeat the important correctness condition that direct TTL purging should be used only when writes have the same TTL setting. The API does not enforce that condition. The filter is designed for Cassandra-formatted values only; applying it to arbitrary values would corrupt or fail compaction behavior.

Test signals: functional tests load the filter and factory by name and verify configured option values through `GetOptions<CassandraOptions>()`.
