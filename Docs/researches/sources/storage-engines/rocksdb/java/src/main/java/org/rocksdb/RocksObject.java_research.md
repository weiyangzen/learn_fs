# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksObject.java

## Purpose
`RocksObject` is the preferred base class for Java wrappers around immutable native RocksDB pointers. It provides stable handle storage and delegates native deletion to subclasses.

## Important APIs and Types
- Extends `AbstractImmutableNativeReference`.
- Protected final `nativeHandle_`.
- Constructor marks the wrapper as owning by default.
- `disposeInternal()` delegates to abstract `disposeInternal(long)`.
- `getNativeHandle()` exposes the pointer.

## Control Flow
Subclasses call the constructor with a native pointer. Close behavior is inherited from `AbstractImmutableNativeReference`; when disposal is needed, it invokes the no-arg `disposeInternal`, which passes the immutable handle to subclass-specific native deletion code.

## State and Persistence Behavior
The class stores a stable native pointer and inherited ownership state. It does not persist data itself, but many subclasses wrap persistent resources such as databases, column-family handles, snapshots, options, envs, and managers.

## Dependencies and Integration Points
It depends on `AbstractImmutableNativeReference` and is used broadly across RocksJNI as the base for native-backed objects. `RocksDB` extends it directly.

## Risks
The public `getNativeHandle()` can expose raw native pointers to package consumers or external callers, making lifecycle misuse possible. Subclasses must correctly disown borrowed handles to prevent double-free and must implement disposal for the exact native type.

## Test Signals
Tests should focus on subclass lifecycle: owned close calls native dispose once, disowned handles do not dispose, immutable handle remains stable, and native handle exposure matches expected pointer values.
