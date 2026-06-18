# sources/storage-engines/foundationdb/fdbserver/logrouter/include/fdbserver/logrouter/LogRouter.h

## Purpose
This public header exposes the log router actor entry point to other fdbserver components.

## Important APIs, Types, And Functions
It forward-declares `InitializeLogRouterRequest` and `ServerDBInfo`, includes `TLogInterface` and Flow, and declares `Future<Void> logRouter(TLogInterface interf, InitializeLogRouterRequest req, Reference<AsyncVar<ServerDBInfo> const> db)`.

## Control Flow
Callers recruit a log router by invoking `logRouter` with the worker's TLog interface, initialization request, and live database-info variable. The returned actor runs until cancellation, removal, or a non-suppressed error.

## State And Persistence Behavior
This header owns no state. Runtime buffering, pop state, and configuration tracking are implemented in `LogRouter.cpp`.

## Dependencies And Integration Points
The API is intentionally narrow and integrates with the core TLog interface and cluster `ServerDBInfo`. CMake publishes this header through the logrouter include directory.

## Risks And Test Signals
The function takes `TLogInterface` and request by value, so callers must provide fully initialized endpoint and recovery metadata. Link tests and actor integration tests should verify inclusion from other targets and correct startup/shutdown behavior.
