<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ReferenceCountedDB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ReferenceCountedDB.java

## Purpose

`ReferenceCountedDB` wraps a per-container `DatanodeStore` with reference counting so `ContainerCache` can share handles safely and close them only when unused. The complete 93-line file was read.

## Important APIs, Types, and Functions

The class extends `DBHandle`. Public methods are `getReferenceCount`, `incrementReference`, `decrementReference`, `cleanup`, `close`, and `isClosed`.

## Control Flow

Callers receive a handle from `ContainerCache.getDB`, which increments the reference. `close` decrements the count and asserts it does not go negative. `cleanup` stops the underlying store when it is already closed or the reference count is zero; otherwise it returns false so eviction/removal can be blocked. Trace logging can include stack traces on refcount changes.

## State and Persistence Behavior

Runtime state is an `AtomicInteger` reference count. Persistent DB contents live in the wrapped store. `cleanup` stops the store, closing RocksDB resources, but does not delete on-disk data.

## Dependencies and Integration Points

It depends on `DBHandle`, `DatanodeStore`, Guava preconditions, and `ContainerCache`.

## Risks and Edge Cases

Reference leaks keep DBs open and block cache eviction. Double close triggers a precondition failure. `cleanup` calls `getStore().stop()` if the store exists and is closed or refcount is zero; callers should not pass null stores. Trace stack capture is expensive and should stay trace-only.

## Test Signals

Tests should cover increment/decrement, negative refcount prevention, cleanup false with active references, cleanup true at zero references, already-closed store behavior, and integration with cache eviction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ReferenceCountedDB.java -->
