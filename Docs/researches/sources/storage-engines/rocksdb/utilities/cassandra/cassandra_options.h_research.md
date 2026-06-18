## `sources/storage-engines/rocksdb/utilities/cassandra/cassandra_options.h`

Purpose: defines shared Cassandra configuration used by the merge operator, compaction filter, and object registry. It is the options payload exposed through RocksDB configurable-object infrastructure.

Important APIs and types: `CassandraOptions` has `kName()`, constructor, `operands_limit`, `gc_grace_period_in_seconds`, and `purge_ttl_on_expiration`. The header also declares C-linkage `RegisterCassandraObjects(ObjectLibrary&, const std::string&)`.

Control flow represented by declarations: producers construct `CassandraOptions` with merge operand limits, tombstone GC grace period, and TTL purge policy. `RegisterCassandraObjects` is called by RocksDB object-library loading to register Cassandra merge/filter classes.

State and persistence behavior: the struct is runtime configuration only. It affects persistent output indirectly by limiting merge behavior and deciding whether expired columns become tombstones or are purged during compaction.

Dependencies and integration: includes RocksDB namespace support and forward declares `ObjectLibrary`. `cassandra_compaction_filter.cc` registers two of these fields for compaction filter/factory option parsing; merge operator code outside this work item uses `operands_limit`.

Risks: `purge_ttl_on_expiration` comment documents a correctness hazard: direct purge can bring old data back unless TTL settings are uniform. The constructor requires all values and provides no default constructor, so option-registration code must create valid initial values.

Test signals: `cassandra_functional_test.cc` verifies parsed options for merge operator, compaction filter, and compaction filter factory.
