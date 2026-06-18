# sources/storage-engines/rocksdb/memory/memory_allocator_test.cc

Purpose: C++ tests for `MemoryAllocator` factories, allocation, option parsing, and block-cache integration.

Important APIs/types/functions: parameterized `MemoryAllocatorTest`, tests `Allocate`, `CreateAllocator`, `DatabaseBlockCache`, `CreateMemoryAllocatorTest.JemallocOptionsTest`, `NewJemallocNodumpAllocator`.

Control flow and state: each parameter attempts `MemoryAllocator::CreateFromString` and records expected support. Supported allocators allocate/deallocate 1024 bytes and report usable size. String creation tests serialize via `ToString` and recreate. Database test configures an LRU block cache with the allocator, writes/flushes 200 keys, reads them back, and asserts cache usage grew. Jemalloc tests validate default options, invalid tcache bounds when limiting is enabled, accepted bounds when limiting disabled, and helper construction.

State and persistence behavior: creates a temporary DB for cache integration and destroys it. Allocator state is process-local.

Dependencies and integration points: `NewLRUCache`, block-based table factory, DB open/put/flush/get, optional jemalloc and memkind builds.

Risks: unsupported optional allocators are bypassed. Cache usage threshold is coarse and may depend on block/cache metadata. TODO notes lite mode incompatibility because tests rely on object creation by string.

Test signals: solid coverage for default allocator and conditional specialized allocators in factory and cache paths.
