# sources/storage-engines/foundationdb/bindings/c/test/unit/fdb_api.hpp

## Purpose
`unit/fdb_api.hpp` declares the RAII wrapper classes implemented in `fdb_api.cpp`. It provides typed future wrappers and a transaction wrapper to make C API unit tests shorter and safer.

## Important APIs, Types, and Functions
- `Future` base class declares destructor and common future methods.
- Typed future classes declare result-specific `get` methods and restrict constructors to friend classes.
- `Result` and `KeyValueArrayResult` wrap newer `FDBResult` APIs.
- `Database` declares static administrative wrappers.
- `Transaction` declares wrappers for transaction lifecycle, options, reads, ranges, mapped ranges, watches, commits, error handling, mutations, committed version, and conflict ranges.

## Control Flow
Tests include this header, select/setup the FDB API separately, create a `Transaction` from an `FDBDatabase*`, call methods returning typed futures, block/get results, and rely on destructors for cleanup.

## State and Persistence Behavior
The declarations define ownership of raw `FDBFuture*`, `FDBResult*`, and `FDBTransaction*`. Persistence is indirect through transaction commit and database admin operations.

## Dependencies and Integration Points
It defines `FDB_USE_LATEST_API_VERSION`, includes `foundationdb/fdb_c.h`, and uses `std::string_view` for key/value parameters. It is test-local and distinct from the production `bindings/c/test/fdb_api.hpp` wrapper used by Mako/shim tests.

## Risks
The header does not delete copy constructors or assignment operators, which undermines unique ownership. The base destructor is pure virtual but implemented in the cpp. `KeyValueArrayResult` comment has a typo but behavior is unaffected. The wrapper is broad enough that API changes require updating declaration and implementation together.

## Test Signals
Compilation of all unit tests using this header is the first signal. Runtime tests should validate automatic cleanup and typed getters for representative C API futures.
