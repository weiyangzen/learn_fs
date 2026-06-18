# sources/storage-engines/rocksdb/memory/memkind_kmem_allocator.cc

Purpose: Implementation of a `MemoryAllocator` backed by memkind DAX KMEM when RocksDB is built with `MEMKIND`.

Important APIs/types/functions: `PrepareOptions`, `Allocate`, `Deallocate`, `UsableSize`.

Control flow and state: `PrepareOptions` checks compile-time support, then delegates to base allocator preparation. Under `MEMKIND`, `Allocate` calls `memkind_malloc(MEMKIND_DAX_KMEM, size)` and throws `std::bad_alloc` on null. `Deallocate` frees through `memkind_free`; usable size delegates to memkind when available.

State and persistence behavior: no internal state; allocations are process memory from the configured memkind.

Dependencies and integration points: memkind library, `BaseMemoryAllocator`, memory allocator factory registration.

Risks: unavailable unless compiled with memkind. Allocation failure throws rather than returning null. Behavior depends on DAX KMEM availability/configuration.

Test signals: memory allocator tests instantiate it conditionally and use it in block cache when supported.
