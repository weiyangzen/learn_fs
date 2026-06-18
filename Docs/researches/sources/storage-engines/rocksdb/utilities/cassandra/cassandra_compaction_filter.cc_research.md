## `sources/storage-engines/rocksdb/utilities/cassandra/cassandra_compaction_filter.cc`

Purpose: implements Cassandra row-value compaction filtering and object-library registration for Cassandra merge/filter components. The filter removes or rewrites expired columns and tombstones during RocksDB compaction.

Important APIs and functions: `cassandra_filter_type_info` describes configurable options for RocksDB's options registry. `CassandraCompactionFilter` constructor stores options and registers them for introspection. `FilterV2()` deserializes `RowValue`, either removes expired columns or converts them to tombstones depending on `purge_ttl_on_expiration`, removes collectable tombstones when the input is a normal `kValue`, and returns remove/change/keep decisions. `CassandraCompactionFilterFactory` creates filters with stored options. `RegisterCassandraObjects()` registers factories for `CassandraValueMergeOperator`, `CassandraCompactionFilter`, and `CassandraCompactionFilterFactory`.

Control flow: `FilterV2()` always deserializes the existing value into a Cassandra `RowValue`. It first handles TTL expiry according to policy, then applies tombstone GC only for compacted full values, not merge operands. Empty compacted rows are removed. Non-empty changed rows are serialized into `new_value`; unchanged rows are kept.

State and persistence behavior: persistent RocksDB values are rewritten from serialized Cassandra row format to either a changed row format or removed. The filter's only state is `CassandraOptions`, including GC grace period and TTL purge policy.

Dependencies and integration: depends on RocksDB compaction filter APIs, object registry/options type reflection, Cassandra `format.h`, and Cassandra merge operator registration. It is loaded dynamically in tests through `ConfigOptions.registry->AddLibrary()`.

Risks: deserialization assumes all values reaching the filter are valid Cassandra row values. Enabling `purge_ttl_on_expiration` is explicitly dangerous unless all writes share the same TTL behavior because purging expired columns can allow older values to reappear. `FilterV2()` ignores `skip_until` and level/key. Default registered factory instances use zeroed options unless overridden by string configuration.

Test signals: `cassandra_functional_test.cc` verifies compaction conversion to tombstones, purging expired columns, row removal when all columns expire, tombstone GC after grace period, tombstone removal from put values, and registry loading/configuration.
