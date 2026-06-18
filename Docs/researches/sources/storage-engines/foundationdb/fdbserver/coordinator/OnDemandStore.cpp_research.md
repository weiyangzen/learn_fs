# sources/storage-engines/foundationdb/fdbserver/coordinator/OnDemandStore.cpp

## Purpose
Implements a lazy wrapper around the coordinator key-value store. The store is opened only when a caller first needs it, which lets coordinator processes avoid creating persistent files until coordination state is actually used.

## Important APIs, Types, and Functions
- `OnDemandStore::open()` creates the backing directory, constructs `keyValueStoreMemory(joinPath(folder, prefix), myID, 500e6)`, and wires its error future into the wrapper promise.
- `get()` and `operator->()` lazily open and return the `IKeyValueStore`.
- `exists()` detects already-created store files, including disk queue files and legacy `.fdb` file names.
- `getError()`, `onClosed()`, `dispose()`, and `close()` implement `IClosable` behavior.

## Control Flow
Construction records folder, UID, and prefix without touching disk. The first `get()` or `operator->()` call opens the store. Destruction calls `close()`, which closes and clears the raw store pointer if it exists. `dispose()` uses the underlying store disposal path and also clears the pointer.

## State and Persistence Behavior
The object owns a raw `IKeyValueStore*` and a `Promise<Future<Void>>` for store errors. The backing files live under `folder` with the supplied prefix. `exists()` is used by coordinator startup to decide whether persistent forwarding state needs to be loaded before any lazy open.

## Dependencies and Integration Points
The implementation uses Flow platform helpers, async file/store APIs, and `keyValueStoreMemory`. It is used by `Coordination.cpp` for generation-register data, forwarding records, and cluster-key rewrites.

## Risks and Edge Cases
`onClosed()` assumes the store is already open and dereferences `store`, so callers must not use it before `get()`. The wrapper is non-copyable but uses a raw pointer, so ownership is manual and must remain single-owner. The fixed memory limit passed to `keyValueStoreMemory` is part of coordinator-store behavior.

## Test Signals
No unit tests are embedded here. Indirect signals are coordinator tests and simulations that start coordinators with empty stores, existing disk-queue files, close/dispose paths, and store error propagation.
