# sources/storage-engines/rocksdb/memory/jemalloc_nodump_allocator.h

Purpose: Declaration and build gating for `JemallocNodumpAllocator`.

Important APIs/types/functions: class `JemallocNodumpAllocator`, `kClassName`, `Name`, `IsSupported`, `IsMutable`, `PrepareOptions`, allocation overrides, jemalloc hook helpers, `original_alloc_`, `per_arena_hooks_`, `tcache_`, `arena_indexes_`.

Control flow and state: compile-time macros enable implementation only when RocksDB is built with jemalloc on POSIX with jemalloc major version >= 5 and `MADV_DONTDUMP`. The allocator is mutable until prepared, then holds arena and hook state.

State and persistence behavior: manages process heap arenas and thread-local tcaches; no persisted state.

Dependencies and integration points: `BaseMemoryAllocator`, `JemallocAllocatorOptions`, object registry/factory path, jemalloc helper headers.

Risks: conditional compilation means methods only exist under support macros; callers must check support. Static hook storage is shared across allocator instances.

Test signals: support-dependent tests instantiate and validate options/allocation.
