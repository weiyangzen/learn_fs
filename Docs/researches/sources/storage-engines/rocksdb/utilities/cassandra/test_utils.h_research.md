# sources/storage-engines/rocksdb/utilities/cassandra/test_utils.h

## Purpose
This header declares reusable helpers and constants for testing Cassandra row-value serialization and merge behavior.

## Important APIs, Types, and Functions
It declares static data constants, column kind constants, `CreateTestColumn`, `CreateTestColumnSpec`, `CreateTestRowValue`, `CreateRowTombstone`, `VerifyRowValueColumns`, `ToMicroSeconds`, and `ToSeconds`.

## Control Flow
The header has no runtime flow; it defines the test helper contract used by Cassandra test files.

## State and Persistence Behavior
The declared constants are defined in the `.cc` file and provide stable backing storage for test column values. Helper-created rows are ordinary `RowValue` objects that can be serialized into persistent-format bytes.

## Dependencies and Integration Points
It includes the RocksDB test harness and Cassandra format/serialize headers. It integrates tests with the production Cassandra row model without exposing these helpers to production code.

## Risks and Edge Cases
Because the header includes the test harness, it should remain test-only. Any change to helper constants or timestamp conversion can alter expected test semantics. Callers depend on the tuple layout for column specs.

## Test Signals
Indirect signal comes from all tests that include this header. Compile failures catch signature drift between helpers and production Cassandra classes.
