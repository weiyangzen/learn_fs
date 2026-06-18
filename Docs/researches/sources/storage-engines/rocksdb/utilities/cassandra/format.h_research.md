# sources/storage-engines/rocksdb/utilities/cassandra/format.h

## Purpose
This header declares the in-memory representation and binary layout contract for Cassandra row values stored in RocksDB merge operands. It documents the row tombstone fields, column masks, normal/expiring/tombstone column layouts, and the merge-facing `RowValue` API.

## Important APIs, Types, and Functions
`ColumnTypeMask` defines `DELETION_MASK` and `EXPIRATION_MASK`. `ColumnBase` is the abstract common interface for column-like values, exposing `Timestamp`, `Mask`, `Index`, `Size`, `Serialize`, and static `Deserialize`. `Column`, `Tombstone`, and `ExpiringColumn` implement the concrete wire layouts. `Columns` aliases a vector of shared column pointers.

`RowValue` exposes constructors for row tombstones and live rows, move-only ownership, binary sizing and serialization, expiration/tombstone cleanup helpers, static deserialization, and static multi-row merge. `get_columns()` exposes the stored column vector for tests and callers that need direct inspection.

## Control Flow
The header itself has no implementation flow, but the declared API implies a two-stage parse: row-level deletion fields first, then zero or more columns selected by mask. The merge API accepts a vector of row values and returns a newly assembled row based on timestamps and tombstone visibility.

## State and Persistence Behavior
The classes model persisted binary records. `RowValue` owns a vector of shared column objects, while `Column` stores a pointer to the value bytes rather than owning a copy. Row tombstones have no columns and use deletion metadata as their last-modified time. Live rows use default deletion sentinels and track a cached last-modified timestamp.

## Dependencies and Integration Points
The declarations depend on RocksDB namespace and merge-related headers, plus standard `chrono`, `memory`, and `vector`. They are consumed by the Cassandra merge operator, test utilities, and serialization tests. The documented layout must remain compatible with persisted RocksDB values and merge operands.

## Risks and Edge Cases
The header exposes mutable implementation assumptions: raw value pointers, signed integer field sizes, and timestamp units. `get_columns()` returns a non-const method exposing a const reference, which is useful in tests but leaks representation. Any change in field order, size, mask interpretation, or sentinel defaults is a storage-format compatibility change.

## Test Signals
The best signals are exact serialization byte tests, row round-trip tests, merge behavior tests, and compaction tests using `CassandraValueMergeOperator`. Review should also check that new column types or mask bits do not accidentally route to existing concrete classes.
