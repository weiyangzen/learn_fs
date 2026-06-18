# sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c_internal.h

## Purpose
`fdb_c_internal.h` declares non-public C API hooks used internally by FoundationDB components for shared database state and future protocol-version testing.

## Important APIs, Types, And Functions
- Forward declaration `DatabaseSharedState`.
- `fdb_database_create_shared_state(FDBDatabase* db)` returns a future for database shared state.
- `fdb_database_set_shared_state(FDBDatabase* db, DatabaseSharedState* p)` installs shared state on a database.
- `fdb_future_get_shared_state(FDBFuture* f, DatabaseSharedState** outPtr)` extracts shared state from a future.
- `fdb_use_future_protocol_version()` switches the client API into future protocol-version mode.

## Control Flow
Callers include this header when they need internal-only hooks. Implementations in `fdb_c.cpp` cast the opaque database/future handles and call internal `IDatabase`/API methods.

## State And Persistence Behavior
The functions affect client process state and database shared state references, not user key/value persistence. `fdb_use_future_protocol_version()` affects protocol selection behavior in the client process.

## Dependencies And Integration Points
It includes `flow/ProtocolVersion.h` and `fdb_c_types.h`, and is passed to `symbolify.py` on Apple so internal exported `fdb_` symbols can be included when required.

## Risks And Edge Cases
These functions are not part of the public stable surface. Misuse can cross database/shared-state lifetimes or force unsupported protocol behavior. Error handling is thin in `fdb_database_set_shared_state()`, which swallows exceptions.

## Test Signals
Internal and upgrade tests using future protocol versions or shared database state provide coverage. Apple exported-symbol generation also validates declaration format.
