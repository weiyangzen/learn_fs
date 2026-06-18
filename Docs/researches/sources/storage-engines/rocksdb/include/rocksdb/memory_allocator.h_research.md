# Research: sources/storage-engines/rocksdb/include/rocksdb/memory_allocator.h

## Purpose

`memory_allocator.h` declares RocksDB's pluggable allocation interface for cache and table/block memory. It lets applications replace default heap allocation with custom allocators, including jemalloc-backed no-core-dump allocation for large caches.

## Important APIs, Types, and Functions

`MemoryAllocator` extends `Customizable` and exposes `Allocate(size_t)`, `Deallocate(void*)`, `UsableSize(void*, size_t)`, `CreateFromString`, `Type`, and `GetId`. `JemallocAllocatorOptions` configures tcache size limiting, lower/upper tcache bounds, and number of jemalloc arenas. `NewJemallocNodumpAllocator` constructs a jemalloc allocator that applies `MADV_DONTDUMP` to allocated cache memory when supported.

## Control Flow

Caches and block/table readers receive a shared allocator from cache options. Allocation paths call `Allocate`, use the returned memory for blocks or metadata, optionally inspect `UsableSize`, and later call `Deallocate` through cache/block deleters. `MemoryAllocator::CreateFromString` registers built-ins once and loads a managed object from the object registry. `NewJemallocNodumpAllocator` is used directly by db_bench and by configurations that request that allocator.

## State and Persistence Behavior

Allocators manage process memory only. The no-dump jemalloc allocator creates dedicated arenas and marks allocations outside core dumps, reducing persisted crash-dump footprint rather than changing DB contents. Allocator instances can carry internal counters, arena handles, tcache configuration, and wrapped target allocators.

## Dependencies and Integration Points

The header depends on `Customizable` and `Status`. Implementations live under `memory/`, with helpers in `utilities/memory_allocators.h`. Integration points include `advanced_cache.h`, `cache.h`, block fetcher, block-based table reader, meta-block loading, `IODispatcher`, C API cache allocator setters, options/customizable tests, db_bench cache options, and table/block fetcher tests.

## Risks and Edge Cases

All methods must be thread-safe because caches and readers call them concurrently. `Deallocate` must pair with the same allocation family; mixing allocators can corrupt memory. `UsableSize` defaults to the requested allocation size, which is conservative but may underreport real allocator capacity. Jemalloc no-dump support depends on build and platform features, so creation can fail. Tcache and arena settings trade memory footprint against contention and must be tuned for thread count and block size.

## Test Signals

Tests include `memory/memory_allocator_test.cc`, block fetcher allocator accounting, `BlockBasedTableTest.MemoryAllocator`, options/customizable allocator loading, and C API allocator wiring. Useful signals are allocation/deallocation balance, nonzero custom allocator usage, successful CreateFromString for built-ins, graceful failure when jemalloc support is unavailable, and absence of leaks or mismatched frees under cache eviction.
