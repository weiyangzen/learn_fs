<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ThreadSafeTransaction.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ThreadSafeTransaction.h

## Purpose
`ThreadSafeTransaction.h` declares thread-safe implementations of the generic client API interfaces. These wrappers serialize operations onto the FoundationDB network thread while exposing `IDatabase`, `ITransaction`, and `IClientApi` to callers that may originate outside the network thread.

## Important APIs, Types, and Functions
Main types are `ThreadSafeDatabase`, `ThreadSafeTransaction`, and `ThreadSafeApi`. Database methods include transaction creation, database options, main-thread busyness, server protocol, connection status, worker reboot, forced recovery, snapshots, shared state, and client status. Transaction methods cover reads, ranges, mapped ranges, mutations, conflict ranges, watches, commit, version vector, span context, throttling duration, cost, approximate size, options, deferred errors, retry, reset, and debug tracing. API methods cover version selection, network options, setup/run/stop, database creation, and completion hooks.

## Control Flow
Public calls return `ThreadFuture` objects and dispatch work to the network thread. `ThreadSafeDatabase` owns or wraps a `DatabaseContext`; `ThreadSafeTransaction` owns a `ReadYourWritesTransaction` pointer and an initialization flag. Transaction methods forward to lower-level RYW/Native API operations after crossing the thread boundary. `ThreadSafeApi` manages process-global API version and network lifecycle with a mutex-protected completion-hook list.

## State and Persistence Behavior
The wrappers manage in-memory references to database contexts, transactions, network state, and shared state. They do not persist records directly, but all transaction mutation calls affect database state once committed. Thread safety is provided by serialization and thread-safe reference counting rather than by making the lower-level transaction object independently concurrent.

## Dependencies and Integration Points
The header depends on API/protocol version types, `ReadYourWrites`, thread helpers, cluster interfaces, and `IClientApi`. It is a bridge for C bindings, Java bindings, fdbcli refactoring, and any external-client path that needs a stable thread-safe interface.

## Risks and Edge Cases
Lifetime of raw `DatabaseContext*` and `ReadYourWritesTransaction*` must be controlled carefully. Move construction exists to support actors, which makes initialization-state correctness important. Network lifecycle methods are process-global and can race if callers misuse API setup/run/stop ordering. The fdbcli refactoring constructor from raw RYW transaction is explicitly transitional.

## Test Signals
Useful signals include C API and Java binding integration tests, external-client tests, multi-threaded transaction tests, network setup/stop lifecycle tests, client status tests, and tests that exercise futures completing from non-network threads.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ThreadSafeTransaction.h -->
