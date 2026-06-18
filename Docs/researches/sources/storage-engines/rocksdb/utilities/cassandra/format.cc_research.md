# sources/storage-engines/rocksdb/utilities/cassandra/format.cc

## Purpose
This file implements the Cassandra row-value binary format and merge semantics used by RocksDB's Cassandra merge operator. It serializes/deserializes normal columns, expiring columns, column tombstones, and row tombstones, and it defines how multiple row versions collapse into one latest visible row.

## Important APIs, Types, and Functions
`ColumnBase` stores the shared `mask` and `index` fields, serializes them, and dispatches `Deserialize` to `Tombstone`, `ExpiringColumn`, or `Column` based on `DELETION_MASK` and `EXPIRATION_MASK`. `Column` adds `timestamp`, value length, and a value pointer. `ExpiringColumn` adds TTL handling, expiration checks, and conversion to a `Tombstone`. `Tombstone` stores local deletion time and delete timestamp and can decide whether it is collectable after a GC grace period.

`RowValue` is the central type. It can represent either a row tombstone or a vector of column objects. It exposes `Size`, `IsTombstone`, `LastModifiedTime`, `Serialize`, `Deserialize`, `RemoveExpiredColumns`, `ConvertExpiredColumnsToTombstones`, `RemoveTombstones`, `Empty`, and static `Merge`. Local constants `kDefaultLocalDeletionTime` and `kDefaultMarkedForDeleteAt` distinguish live rows from tombstone rows.

## Control Flow
Deserialization starts by reading row-level deletion fields. If the buffer ends there, a row tombstone is returned. Otherwise the deletion fields must be defaults, and the code repeatedly dispatches column deserialization until the offset reaches the buffer size, computing `last_modified_time` as the max column timestamp.

`RowValue::Merge` sorts input rows by descending `LastModifiedTime`. It iterates from newest to oldest, accumulating the best column per index in a `std::map`. If the newest encountered row is a tombstone before any column is selected, the tombstone wins immediately. If a tombstone is found after newer columns have been selected, its timestamp becomes a cutoff; selected columns whose timestamp is older than or equal to that cutoff are filtered out before the merged row is returned.

## State and Persistence Behavior
Serialization appends a compact binary row image into caller-owned strings. Deserialized `Column` and `ExpiringColumn` instances keep `const char*` pointers into the source buffer for value bytes, so the source buffer must outlive the row objects if they are later serialized or inspected. Expiration and tombstone collectability depend on `std::chrono::system_clock::now()`, making behavior time-dependent.

## Dependencies and Integration Points
The implementation depends on `utilities/cassandra/serialize.h` for big-endian integer encoding, `rocksdb::Slice`-compatible storage through raw buffer pointers, and the merge operator in `merge_operator.cc`. It is also exercised by Cassandra test utilities and any DB configured with `CassandraValueMergeOperator`.

## Risks and Edge Cases
Most validation is via `assert`, so malformed persisted values can become unchecked memory reads in release builds. The use of raw `const char*` value pointers makes lifetime management critical after deserialization. The mask dispatch treats any mask with the deletion bit set as a tombstone even if other bits are present. Time-based expiration can make tests or compactions nondeterministic if timestamps are close to wall clock. The merge algorithm returns an empty live row if all selected columns are hidden by an older row tombstone rather than returning the tombstone itself.

## Test Signals
Expected coverage comes from Cassandra serialization tests and merge-operator tests elsewhere in the suite. Important signals are round-trip row/column encoding, latest-column selection by index, row tombstone cutoff behavior, expired-column removal/conversion, and tombstone GC grace filtering.
