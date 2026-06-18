## `sources/storage-engines/rocksdb/utilities/cassandra/cassandra_functional_test.cc`

Purpose: DB-level integration tests for Cassandra merge operator, compaction filter, and object-registry loading. It validates that serialized `RowValue` merge operands and put values behave correctly through real RocksDB flush, compaction, get, and dynamic option parsing paths.

Important APIs and helpers: `CassandraStore` wraps `DB` with `Append()` using `Merge`, `Put()`, `Flush()`, `Compact()`, and `Get()` returning deserialized `RowValue`. `TestCompactionFilterFactory` creates `CassandraCompactionFilter` instances from test flags. `CassandraFunctionalTest::OpenDb()` creates a fresh DB with `CassandraValueMergeOperator` and the test compaction filter factory.

Control flow: tests append serialized row mutations, optionally flush between operands to force persistent files, then compact and read results. `SimpleMergeTest` checks merge resolution without compaction. TTL compaction tests check conversion to tombstones, direct purge when enabled, complete row removal when all columns expire, tombstone GC after grace period, and tombstone removal from a put value. Registry tests first assert class-name creation fails before registering the Cassandra library, then registers `RegisterCassandraObjects` and validates default and configured objects.

State and persistence behavior: values are persisted in RocksDB as Cassandra row serialization. Merge operands are combined by `CassandraValueMergeOperator`; compaction rewrites or removes rows through `CassandraCompactionFilter`. Tests use a per-thread DB path and destroy it before each test.

Dependencies and integration: uses `DBImpl` test flush/compact helpers, RocksDB DB/options, merge operator APIs, object registry, utility merge operators include, Cassandra compaction filter/merge operator/test utilities, and stack trace test harness.

Risks: time-dependent TTL tests use current time and a generous `kTestTimeoutSecs` to avoid expiry during test execution. The helper prints errors to `stderr` and returns booleans rather than asserting inside wrappers. These tests do not cover malformed Cassandra values or concurrent merges.

Test signals: strong integration coverage for the Cassandra plugin path, especially options string parsing and compaction effects after flush/compaction.
