## `sources/storage-engines/rocksdb/utilities/cassandra/cassandra_format_test.cc`

Purpose: unit tests Cassandra row serialization and local compaction helpers. It validates binary layout for columns, expiring columns, tombstones, row tombstones, rows with columns, TTL purging, and TTL-to-tombstone conversion.

Important test cases: `ColumnTest.Column` verifies mask/index/timestamp/size fields, serialization bytes, and deserialization through both `Column` and `ColumnBase`. `ExpiringColumnTest.ExpiringColumn` adds TTL serialization. `TombstoneTest.TombstoneCollectable` validates GC grace timing, and `TombstoneTest.Tombstone` validates deletion-time and marked-for-delete layout. `RowValueTest.RowTombstone` verifies row tombstone layout. `RowValueTest.RowWithColumns` validates row metadata sentinels and ordered serialized columns. TTL tests validate `RemoveExpiredColumns()` and `ConvertExpiredColumnsToTombstones()`.

Control flow: tests construct small in-memory rows using real constructors and test utilities, serialize into strings, manually deserialize primitive fields by offset, then run class deserializers and reserialize to assert byte-for-byte equality. TTL tests use `time(nullptr)`, helper constants, and verification helpers to compare resulting column types/indexes/timestamps.

State and persistence behavior: the tests define the expected persistent byte layout for Cassandra value format. Any production format change should break these tests unless migration/compatibility is added.

Dependencies and integration: uses RocksDB test harness, Cassandra `format.h`, `serialize.h`, and `test_utils.h`. The `main()` installs stack trace handling and runs GoogleTest.

Risks: several tests depend on wall-clock `time(nullptr)`, but only relative comparisons are used. The test name `PurgeTtlShouldRemvoeAllColumnsExpired` has a typo but still compiles. Coverage focuses on happy-path deserialization and does not test malformed byte strings or overflow/truncation behavior.

Test signals: this file is itself the test signal for Cassandra wire format and local row cleanup semantics.
