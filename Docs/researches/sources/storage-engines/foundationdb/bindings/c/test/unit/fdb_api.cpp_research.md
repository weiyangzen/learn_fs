# sources/storage-engines/foundationdb/bindings/c/test/unit/fdb_api.cpp

## Purpose
`unit/fdb_api.cpp` implements RAII C++ wrappers around selected FoundationDB C API futures, results, database management functions, and transaction methods for use in unit tests.

## Important APIs, Types, and Functions
- `Future` destructor destroys `FDBFuture`; methods wrap readiness, blocking, callbacks, error retrieval, memory release, and cancellation.
- Typed futures implement `get` methods for int64, double, key, value, string array, key-value array, mapped key-value array, and key-range array.
- `Result` and `KeyValueArrayResult` manage `FDBResult`.
- `Database` static methods wrap administrative futures.
- `Transaction` constructor/destructor manage `FDBTransaction`; methods wrap options, read version, approximate size, costs, reads, ranges, mapped ranges, watch, commit, on_error, mutations, committed version, and conflict ranges.

## Control Flow
Tests create wrapper objects on the stack. Constructors allocate C API handles; destructors clean them up. Methods return typed future wrappers by value so future cleanup is tied to object lifetime. Fatal transaction construction errors print and abort.

## State and Persistence Behavior
Wrappers own native handles. Transaction methods can read or mutate database state depending on caller commits. Future/result objects own C API memory and release on destruction.

## Dependencies and Integration Points
It depends on `fdb_api.hpp`, the FoundationDB C API, and iostream for fatal construction errors. Unit tests such as disconnected timeout tests use these wrappers to avoid repetitive destroy calls.

## Risks
Wrappers are copyable by default because copy/move constructors are not deleted; copying a `Future`, `Result`, or `Transaction` could double-destroy native handles. Return-by-value relies on copy elision/move behavior but explicit copy remains dangerous. Constructor aborts instead of returning errors, which is acceptable for tests but not library-grade.

## Test Signals
Wrapper use in unit tests exercises common paths. Additional compile/runtime tests should forbid copying and cover every typed getter with a real or mocked future result.
