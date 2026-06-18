# sources/storage-engines/foundationdb/fdbclient/LocalClientAPI.cpp

## Purpose
`LocalClientAPI.cpp` exposes the in-process FoundationDB client API implementation. It returns a singleton `ThreadSafeApi` through the `IClientApi` interface for local callers.

## Important APIs, Types, And Functions
The only function is `getLocalClientAPI()`. It declares a function-local static `IClientApi*` initialized with `new ThreadSafeApi()` and returns that pointer on every call.

## Control Flow
The first call constructs the `ThreadSafeApi`; subsequent calls return the same pointer. There is no explicit teardown.

## State And Persistence Behavior
State is process-global singleton client API state owned for the lifetime of the process. The file does not mutate database contents directly; callers use the returned API to open databases and create transactions.

## Dependencies And Integration Points
It includes `LocalClientAPI.h` and `fdbclient/ThreadSafeTransaction.h`. It integrates with components that need a local `IClientApi` implementation without loading an external C API boundary.

## Risks And Edge Cases
The singleton is intentionally leaked to avoid shutdown-order problems. Any `ThreadSafeApi` initialization failure would surface on first call. The raw pointer contract assumes callers do not delete it.

## Test Signals
Compile/link tests should verify the symbol is present and returns a non-null `IClientApi*`. Integration tests should exercise basic database/transaction operations through the returned thread-safe API.
