# sources/storage-engines/rocksdb/utilities/cassandra/test_utils.cc

## Purpose
This file implements helpers for Cassandra row-value tests. It creates deterministic normal columns, tombstone columns, expiring columns, row tombstones, and assertion helpers for column contents.

## Important APIs, Types, and Functions
It defines test constants `kData`, `kExpiringData`, `kTtl`, and mask/index constants `kColumn`, `kTombstone`, and `kExpiringColumn`. `CreateTestColumn` constructs the appropriate `ColumnBase` subclass based on the mask. `CreateTestColumnSpec` packages a mask/index/timestamp tuple. `CreateTestRowValue` builds a live `RowValue` from specs and computes the max timestamp. `CreateRowTombstone` builds a row tombstone. `VerifyRowValueColumns` compares timestamp, mask, and index. `ToMicroSeconds` and `ToSeconds` convert timestamp units.

## Control Flow
The main branch point is `CreateTestColumn`: deletion masks create `Tombstone`, expiration masks create `ExpiringColumn`, and all other masks create `Column`. `CreateTestRowValue` loops over specs, constructs each column, updates `last_modified_time`, and returns a moved row value.

## State and Persistence Behavior
All helper-generated column value pointers point at file-scope static arrays, so their lifetime is stable for tests. Timestamps are interpreted as microseconds for column timestamps and converted to seconds for local deletion time.

## Dependencies and Integration Points
These helpers depend on `format.h`, `serialize.h`, and RocksDB's test harness. They are meant to reduce duplication in Cassandra format and merge tests.

## Risks and Edge Cases
The helper uses masks rather than the exported `kColumn`/`kTombstone`/`kExpiringColumn` constants to choose the concrete type, so callers must pass mask bits correctly. The test data sizes include raw array lengths and no terminating nulls. `ToSeconds` truncates microseconds, matching Cassandra local deletion time but potentially surprising in tests near second boundaries.

## Test Signals
This file is support code, not a test itself. Its correctness is visible through Cassandra format/merge tests that assert column ordering, timestamp selection, row tombstones, and TTL behavior.
