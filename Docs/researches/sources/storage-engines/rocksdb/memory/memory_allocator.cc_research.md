# sources/storage-engines/rocksdb/memory/memory_allocator.cc

Purpose: Registers built-in `MemoryAllocator` implementations and implements string-based allocator creation.

Important APIs/types/functions: `MemoryAllocatorWrapper`, `MemoryAllocator::CreateFromString`, `RegisterBuiltinAllocators`, factories for `DefaultMemoryAllocator`, `CountedMemoryAllocator`, `JemallocNodumpAllocator`, `MemkindKmemAllocator`.

Control flow and state: a static `once_flag` ensures built-in factories are registered once in the default object library. `CreateFromString` copies config options, enables prepare-options invocation, and calls `LoadManagedObject`. Wrapper type info allows nested `target` allocator configuration.

State and persistence behavior: process-global object registry state; no persistent files.

Dependencies and integration points: RocksDB customizable options/object registry, utility memory allocators, jemalloc/memkind allocator classes, cache/table options.

Risks: unsupported optional allocators return null from factories with an error message. String parsing depends on the customizable object framework. Registry is global and long-lived.

Test signals: `memory_allocator_test.cc` validates creation, string round-trip, unsupported behavior, and block cache integration.
