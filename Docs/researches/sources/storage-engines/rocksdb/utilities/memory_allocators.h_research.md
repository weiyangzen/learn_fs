# sources/storage-engines/rocksdb/utilities/memory_allocators.h

## Purpose
This header provides simple `MemoryAllocator` implementations and wrappers used by RocksDB components and tests: a default new/delete allocator, a failing base class for conditionally compiled allocators, a wrapper/decorator, and a counted allocator.

## Important APIs, types, and functions
`DefaultMemoryAllocator` implements `Allocate(size_t)` with `new char[size]`, `Deallocate(void*)` with `delete[]`, and reports `Name()` as `"DefaultMemoryAllocator"`.

`BaseMemoryAllocator` implements failure-mode `Allocate()` and `Deallocate()` with `assert(false)`, intended as a base for optional allocators that only provide real behavior when a compile-time feature is enabled.

`MemoryAllocatorWrapper` owns a `shared_ptr<MemoryAllocator>` target, delegates `Allocate`, `Deallocate`, `UsableSize`, and exposes `Inner()`.

`CountedMemoryAllocator` extends the wrapper, defaults to wrapping `DefaultMemoryAllocator`, increments atomic allocation/deallocation counters, returns `GetId()` as its name, and exposes counter getters.

## Control flow
Wrapper methods forward directly to `target_`. Counted methods increment their atomics before delegating. No allocation metadata is stored by the counted wrapper, so it counts calls rather than bytes or live allocations.

## State and persistence behavior
State is in-memory only: `target_` shared ownership plus atomic counters in `CountedMemoryAllocator`.

## Dependencies and integration points
The header depends on `rocksdb/memory_allocator.h` and `<atomic>`. It integrates wherever RocksDB accepts a `MemoryAllocator`, including caches or memory-managed table/block components.

## Risks and edge cases
`BaseMemoryAllocator` will abort in debug builds if used without overrides and return null/do nothing in release after the assert is compiled out. `DefaultMemoryAllocator` provides no alignment beyond `new[]`. Counters can diverge from live allocations when allocations fail or callers deallocate externally allocated memory.

## Test signals
No direct test is listed here. Expected coverage is through allocator users and any tests that inspect counted allocation/deallocation calls.
