# sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/ApplyMetadataMutation.h

## Purpose
Defines the shared metadata-mutation application interface used by commit-proxy, resolver, and related recovery/configuration code. It intentionally avoids depending on the full commit-proxy data structure by exposing narrow context structs.

## Important APIs, Types, And Functions
`ApplyMetadataRangeLock` abstracts pending range-lock request handling. `ApplyMutationsData` tracks an apply worker, end version, and key-version map. `ApplyMetadataProxyContext` packages proxy-side state such as transaction state store, backup key map, server cache, commit stream, committed version, storage cache, popped tags, TSS mapping, checksum builder, epoch, and optional range lock. `ResolverData` packages resolver-side fields including `LogSystemConsumer`, `LogPushData`, pop version, and caches. Functions include `isMetadataMutation()`, `getStorageInfo()`, overloads of `applyMetadataMutations()`, and `containsMetadataMutation()`.

## Control Flow
Callers first detect system-key mutations using `isMetadataMutation()` or `containsMetadataMutation()`. Proxy or resolver code then calls the appropriate `applyMetadataMutations()` overload with an arena, span context, version, pop version, and context. The concrete implementation, outside this header, applies system-key changes to transaction state, storage metadata, backup metadata, log-system pop state, and configuration-change signals.

## State And Persistence Behavior
The header defines pointers/references to persistent or semi-persistent state: `IKeyValueStore` transaction state, `KeyRangeMap` metadata, storage caches, tag popped versions, committed-version notification, and checksum builder. The header itself persists nothing, but its interfaces are used to mutate metadata durable enough to participate in recovery and configuration management.

## Dependencies And Integration Points
Depends on FDB client/server metadata types: `BackupAgent`, `MutationList`, `Notified`, `StorageServerInterface`, `SystemData`, `IKeyValueStore`, `LogProtocolMessage`, `LogSystemConsumer`, and Flow reference utilities. It integrates resolver metadata application with commit-proxy log pushes and cluster-controller style initial/broadcast metadata application.

## Risks And Edge Cases
`isMetadataMutation()` is explicitly conservative: many system-key mutations may be treated as metadata even if not all are processed by the implementation. Most context fields are raw pointers and must outlive the call. Resolver and proxy paths differ in available state, so overload selection and null handling are important. Range-lock and checksum hooks add high-impact side effects if inconsistently wired.

## Test Signals
Test signals are mostly indirect through resolver, commit-proxy, recovery, configuration-change, range-lock, backup, and TSS mapping tests. A useful local signal is whether metadata mutation batches force `confChanges` when expected and whether tag pop versions and transaction-state keys are updated consistently.
