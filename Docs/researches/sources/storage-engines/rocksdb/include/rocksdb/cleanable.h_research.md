# sources/storage-engines/rocksdb/include/rocksdb/cleanable.h

## Purpose

`cleanable.h` defines a small RAII cleanup registry used throughout RocksDB to attach deferred cleanup actions to iterators, pinned slices, async IO buffers, cache handles, and other objects that need lifetime-coupled release callbacks. It also defines `SharedCleanablePtr`, a copyable reference-counted wrapper for a `Cleanable` that allows multiple outer objects to share cleanup ownership efficiently.

## Important APIs, Types, and Functions

`Cleanable` owns a linked list of cleanup records. Each record stores a `CleanupFunction` and two opaque arguments. Public operations include construction/destruction, move construction/assignment, `RegisterCleanup(function, arg1, arg2)`, `DelegateCleanupsTo(Cleanable* other)`, `Reset()`, and `HasCleanups()`. Copy construction and copy assignment are deleted to prevent accidental double execution.

The first cleanup is stored inline in `cleanup_`; additional cleanups are heap-allocated `Cleanup` nodes linked through `next`. The protected `RegisterCleanup(Cleanup* c)` transfers ownership of an existing cleanup node to this object. Private `DoCleanup()` executes the inline function first, then each linked cleanup, deleting heap nodes as it goes. `Reset()` runs cleanup and nulls the inline function/next pointers for reuse.

`SharedCleanablePtr` exposes empty construction, copy/move construction and assignment, destructor, `Allocate()`, `Reset()`, dereference/arrow/get accessors, `RegisterCopyWith(Cleanable* target)`, and `MoveAsCleanupTo(Cleanable* target)`. Its hidden `Impl` carries the refcounted `Cleanable`.

## Control Flow

Cleanup flow is destructor-driven unless `Reset()` is called explicitly. When a `Cleanable` is destroyed, it calls registered functions in registration-list order as encoded by the implementation, then deletes extra cleanup nodes. `DelegateCleanupsTo` moves this object's cleanup chain to another `Cleanable`, extending the target's cleanup set and preventing this object from running them. Move operations transfer cleanup ownership instead of duplicating it.

`SharedCleanablePtr` adds reference-counted flow: only after all copies are gone do the cleanups registered with the pointed-to `Cleanable` execute. `RegisterCopyWith` and `MoveAsCleanupTo` register the shared pointer's eventual destruction as a cleanup on a target object, delaying inner cleanup until the target's cleanup runs.

## State and Persistence Behavior

The state is entirely in-memory: callback pointers, opaque arguments, a linked cleanup list, and a hidden refcount for shared cleanables. It does not persist data, but it protects resources that may represent persistent or external state, such as cache handles, pinned blocks, file buffers, or iterators over DB state. Correct cleanup ordering prevents use-after-free for pinned slices and avoids leaks of cache references or IO allocations.

## Dependencies and Integration Points

The header only depends on `rocksdb/rocksdb_namespace.h`, but it is foundational across the read path. `IteratorBase` and internal iterators derive from `Cleanable`; `PinnableSlice` uses it to pin data and transfer ownership; cache helper utilities register cache handle releases; `GetContext` delegates value-pinner cleanups to pinned iterator managers; `io_dispatcher` uses `SharedCleanablePtr` for shared read-buffer cleanup; transaction code registers iterator cleanup callbacks. `table/cleanable_test.cc` is the direct behavioral test suite.

## Risks and Edge Cases

The biggest risks are double cleanup, missed cleanup, and cleanup cycles. The deleted copy operations avoid one double-free class, but incorrect delegation or manual reuse can still be hazardous. `SharedCleanablePtr` explicitly warns that reference cycles prevent cleanup forever. Callback functions receive untyped `void*` arguments, so type/lifetime mistakes are unchecked. `DoCleanup()` does not reset pointers; only `Reset()` does, so calling cleanup-like paths incorrectly could repeat work if implementation details are bypassed.

Exception safety matters even though this header does not mention exceptions: cleanup callbacks should not throw through destructors. Thread safety is not advertised; users should assume registration and cleanup are externally synchronized unless an owning object provides stronger guarantees.

## Test Signals

`table/cleanable_test.cc` directly covers registration, destructor cleanup, delegation into empty and non-empty targets, `PinnableSlice` interaction, shared wrapping, and `SharedCleanablePtr` behavior. Search signals also show integration coverage in cache helpers, IO dispatcher tests, transaction iterator cleanup, and read-path tests that depend on pinned data remaining valid until cleanups run.
