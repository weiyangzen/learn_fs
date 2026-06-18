# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/IClientApi.h

## Purpose
Defines the top-level abstract client API boundary used by native, dynamically loaded, and multiversion FoundationDB clients. It separates transaction, database, and network lifecycle operations from concrete implementations while preserving C-binding-compatible behavior through thread-safe futures.

## Important APIs, Types, And Functions
`ITransaction` covers read version management, point and range reads, mapped range reads, address lookup, versionstamp retrieval, conflict ranges, mutations, watches, commit, post-commit metadata, cost/size metrics, transaction options, error handling, reset, tracing, printing, and intrusive reference counting. `IDatabase` creates transactions, applies database options, exposes busyness and protocol monitoring, management operations such as reboot/recovery/snapshot, shared-state plumbing, and client status JSON. `IClientApi` selects API version, reports client version, chooses future protocol behavior, manages network setup/run/stop, opens databases from cluster files or connection strings, and registers network-thread completion hooks.

## Control Flow
Callers select/configure the client API, set network options, run the network, create a database, create transactions, then issue transaction methods that return `ThreadFuture` results usable outside the network thread. `onError` and `reset` define retry loops at transaction level. Management methods route through `IDatabase` rather than exposing system-key details to callers.

## State And Persistence Behavior
The interface itself stores no state. Implementations maintain transaction mutation buffers, conflict ranges, watches, database options, network runtime state, shared database state, and cluster connections. Committed mutations, watches, snapshots, worker reboot requests, and force-recovery requests affect cluster state through concrete implementations.

## Dependencies And Integration Points
This header depends on generated option enums, FDB types, tracing span context, protocol versions, and `ThreadFuture`. `MultiVersionTransaction.h` implements this interface for dynamically loaded and multiversion clients; native client code implements it for the built-in client.

## Risks And Test Signals
The main risk is interface drift: every implementation must preserve memory lifetime guarantees for returned `Standalone` values held by `ThreadFuture`, map options correctly, and keep thread-safety promises. Test signals include C API compatibility tests, multiversion client tests, transaction retry tests, range/mapped-range coverage, management command tests, and memory-lifetime tests around future completion and cleanup.
