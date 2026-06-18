# sources/storage-engines/foundationdb/fdbclient/ClusterConnectionKey.h

## Purpose

`ClusterConnectionKey.h` declares the database-key-backed `ClusterConnectionKey` connection record. It adapts a `Database` plus `Key` into the `IClusterConnectionRecord` interface used by cluster coordination and leader-monitoring code.

## Important APIs And Types

`ClusterConnectionKey` inherits from `IClusterConnectionRecord`, `ReferenceCounted<ClusterConnectionKey>`, and `NonCopyable`. Its public API exposes construction from a `Database`, key, connection string, and optional `ConnectionStringNeedsPersisted`; static `loadClusterConnectionKey()`; overrides for `setAndPersistConnectionString()`, `getStoredConnectionString()`, `upToDate()`, `getLocation()`, `makeIntermediateRecord()`, and `toString()`; and reference-count forwarding through `addref()` / `delref()`.

Protected `persist()` performs the virtual persistence hook. Private static actor helpers take a `Reference<ClusterConnectionKey>` so async code can safely retain the object across yields. Private state is the backing `Database`, the `connectionStringKey`, and `lastPersistedConnectionString` used for optimistic concurrency checks.

## Control Flow And State

The header establishes a pattern where public virtual methods are thin wrappers and async work is performed by static methods holding explicit references. The object is non-copyable, reference-counted, and stores only the backing location plus last-known persisted value; actual durable data lives in the target database key.

## Dependencies And Integration Points

It includes `fdbclient/CoordinationInterface.h` for `IClusterConnectionRecord` / `ClusterConnectionString` and `fdbclient/NativeAPI.actor.h` for `Database`, `Transaction`, and `Future` types. It is compiled with the implementation in `ClusterConnectionKey.cpp`.

## Risks And Test Signals

Because this header exposes a reference-counted type through an interface, lifetime correctness depends on every async implementation using `Reference<...>::addRef(this)` before yielding. Interface tests should validate that all virtual methods behave consistently with file and memory connection records and that `getLocation()` / `toString()` are stable for diagnostics.
