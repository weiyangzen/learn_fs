# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksMutableObject.java

## Purpose
`RocksMutableObject` is a base class for native RocksDB wrappers whose native pointer can change after construction. It is deliberately discouraged except when mutability is required because it adds synchronization and ownership complexity.

## Important APIs and Types
- Extends `AbstractNativeReference`.
- Mutable fields: `nativeHandle_` and `owningHandle_`.
- Constructors for empty and owned native handle states.
- Handle mutation: `resetNativeHandle(long, boolean)` and `setNativeHandle(long, boolean)`.
- Lifecycle: synchronized `isOwningHandle()`, `getNativeHandle()`, `close()`, `disposeInternal()`, abstract `disposeInternal(long)`.

## Control Flow
`resetNativeHandle` closes the current owned handle, then installs a new handle and ownership flag. `setNativeHandle` installs without closing first. `close` checks ownership, disposes the current native handle, then clears ownership and sets the handle to zero. All handle operations are synchronized to serialize mutation and close.

## State and Persistence Behavior
The class stores only a pointer and an ownership flag. Persistence behavior belongs to the native object being wrapped. Closing can free native persistent or transient resources depending on subclass implementation.

## Dependencies and Integration Points
It depends on `AbstractNativeReference`. Mutable native wrappers such as slice-like or reusable option objects can extend it when immutable `RocksObject` is insufficient.

## Risks
Calling `setNativeHandle` over an owned live handle leaks unless `resetNativeHandle` is used. `getNativeHandle` relies on an assertion to reject zero handles, so production code may still pass zero to JNI if assertions are disabled and callers misuse it. Subclasses must implement correct native disposal for the dynamic handle type.

## Test Signals
Tests should cover reset closing previous handles, set without close when intentionally borrowed, idempotent close, ownership false close no-op, synchronization under concurrent reset/close, and subclass disposal being called exactly once per owned handle.
