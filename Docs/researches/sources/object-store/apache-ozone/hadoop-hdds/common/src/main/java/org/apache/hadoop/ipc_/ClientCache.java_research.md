# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ClientCache.java

## Purpose
Caches `Client` instances by `SocketFactory` and reference-counts shared IPC clients.

## Important APIs, Types, And Functions
Public methods are `getClient(Configuration, SocketFactory, Class<? extends Writable>)`, overloads with defaults, `stopClient`, and `clearCache`.

## Control Flow
`getClient` synchronizes, creates a new `Client` when no factory entry exists, or increments the existing client's ref count. `stopClient` decrements under lock, removes the client when count reaches zero, and then stops it outside the synchronized block. `clearCache` stops all clients and clears the map.

## State And Persistence
State is a process-local `HashMap<SocketFactory, Client>` and client ref counts. No persistence.

## Dependencies And Integration Points
Used by RPC layers that share IPC clients across protocol proxies. Depends on Hadoop `Configuration`, `Writable`, `ObjectWritable`, and Java `SocketFactory`.

## Risks
Cache keying only by `SocketFactory` means different configurations/value classes can share a client; the comment acknowledges timeout/pooling tradeoffs. `clearCache()` is not synchronized and can race with `getClient`/`stopClient`.

## Test Signals
Tests should verify reuse by factory, ref-count stop behavior, default overloads, config-sharing semantics, and concurrent clear/get behavior.
