# sources/storage-engines/foundationdb/bindings/c/test/fdb_api.hpp

## Purpose
C++ test wrapper around the FoundationDB C API, providing RAII ownership, typed futures, byte/string conversion, and convenience methods for network, database, and transaction operations.

## Important APIs, types, and functions
Defines `Error`, byte aliases, future result traits, `Future`, `TypedFuture`, `Result`, `Transaction`, `Database`, `IDatabaseOps`, key selector helpers, network option/setup wrappers, and API version selection helpers. Native C API symbols are nested under `fdb::native`.

## Control flow
Checked wrapper methods throw on C API errors. `Future::then` allocates a callback lambda and deletes it after invocation. Transactions return typed futures for reads/commits/watches and call mutation APIs for writes.

## State and persistence behavior
Shared pointers own native `FDBFuture`, `FDBTransaction`, `FDBDatabase`, and `FDBResult` handles. Persistence occurs only through committed transaction mutations.

## Dependencies and integration points
Includes generated FDB options and `foundationdb/fdb_c.h`. Used by API tester, client-config tester, shim tests, Mako, and memory tests.

## Risks and test signals
Future/result buffer lifetimes, callback deletion, disabled overflow checks in `intSize`, and atomic handle swaps are key risk areas. Runtime C API workloads validate wrapper compatibility.
