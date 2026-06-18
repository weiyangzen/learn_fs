# sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/RangeQueryTest.java

## Purpose
`RangeQueryTest` unit-tests Java range-query iteration logic using `FakeFDBTransaction` and a fake `Database`, avoiding a live FoundationDB server.

## Important APIs, Types, and Functions
It defines `EXECUTOR`, `makeFakeDatabase`, and parameterized tests over every `StreamingMode`. It uses `Transaction.getRange`, `AsyncIterable.asList`, `ByteArrayUtil`, and `FakeFDBTransaction.getNumRangeCalls`.

## Control Flow
`makeFakeDatabase` returns an anonymous `Database` that creates fake transactions with incrementing dummy native pointers. Tests build deterministic key-value data, open the fake database/transaction, validate an exact `get`, then issue range scans over `"a"` to `"b"` with no row limit, with row limit, reversed with no row limit, and reversed with row limit. Assertions compare returned keys/values and, for limited cases, confirm only one underlying range request.

## State and Persistence Behavior
All data is held in memory in the fake transaction backing map. Database and transaction close/finalize are no-ops. No persistent database state is involved.

## Dependencies and Integration Points
It depends on fake transaction behavior and Java range query iteration logic. It is a fast unit-level complement to live integration range tests.

## Risks and Edge Cases
Because `FakeFDBTransaction` only partially models key selectors and batching, these tests cannot prove native pagination or selector semantics. The fake database leaves many methods unimplemented, so reuse outside these narrow tests would fail.

## Test Signals
Passing indicates the Java-side range iterable returns expected rows for each streaming mode, respects row limits in the fake path, and handles reverse ordering.
