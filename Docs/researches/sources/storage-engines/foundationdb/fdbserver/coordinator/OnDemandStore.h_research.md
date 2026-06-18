# sources/storage-engines/foundationdb/fdbserver/coordinator/OnDemandStore.h

## Purpose
Declares `OnDemandStore`, a small `IClosable` implementation that delays creation of a coordinator-local `IKeyValueStore` until first use.

## Important APIs, Types, and Functions
- Constructor accepts the data folder, local UID, and file prefix.
- `get()` and `operator->()` expose the lazily opened `IKeyValueStore`.
- `exists()` checks for persistent store artifacts without forcing an open.
- `getError()`, `onClosed()`, `dispose()`, and `close()` satisfy the close/error interface.

## Control Flow
The header keeps `open()` private so all callers go through lazy `get()`. The class is `NonCopyable`, preventing accidental multiple owners of the underlying raw store pointer.

## State and Persistence Behavior
Private state is `folder`, `myID`, `store`, `err`, and `prefix`. Persistent behavior is delegated to the concrete key-value store opened by the `.cpp` implementation.

## Dependencies and Integration Points
Includes Flow arena/random/platform headers and `IKeyValueStore`. Coordinator code depends on this type for durable local state while keeping creation cost conditional.

## Risks and Edge Cases
The declaration exposes raw-pointer access to the underlying store, so lifetime remains controlled by the wrapper and callers must not retain the pointer after `close()` or `dispose()`. The error promise is one-shot and tied to the first store open.

## Test Signals
Coverage is indirect through coordinator startup, generation register, and forwarding tests. Useful checks include verifying that `exists()` detects both disk-queue and legacy file layouts without opening a new store.
