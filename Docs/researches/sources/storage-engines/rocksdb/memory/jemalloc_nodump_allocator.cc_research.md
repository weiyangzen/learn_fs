# sources/storage-engines/rocksdb/memory/jemalloc_nodump_allocator.cc

Purpose: Specialized `MemoryAllocator` using jemalloc arenas whose extents are marked `MADV_DONTDUMP`, reducing core-dump footprint.

Important APIs/types/functions: `IsSupported`, constructor/destructor, `PrepareOptions`, `InitializeArenas`, `Allocate`, `Deallocate`, `UsableSize`, `GetArenaIndex`, `GetThreadSpecificCache`, static extent hook `Alloc`, `DestroyArena`, `DestroyThreadSpecificCache`, `NewJemallocNodumpAllocator`.

Control flow and state: support checks compile-time jemalloc/POSIX/MADV availability. `PrepareOptions` validates tcache bounds and arena count, then initializes arenas once. Arena initialization creates jemalloc arenas, copies extent hooks, records original alloc hook, replaces alloc hook with one that calls `madvise(..., MADV_DONTDUMP)`, and stores hook ownership. Allocations choose an arena randomly per thread and optionally create/use a thread-specific tcache. Destruction scrapes/destroys tcaches and arenas.

State and persistence behavior: process memory allocator state only; no persistence. Static original alloc hook is process-wide.

Dependencies and integration points: jemalloc mallctl/mallocx/dallocx, `MemoryAllocator` factory registry, configurable options, thread local pointer utility.

Risks: assumes new jemalloc arenas share the same original alloc hook. Some mallctl failures become `Incomplete`; tcache creation failure silently disables tcache. `madvise` failure asserts and prints stderr. Only available for specific build/platform combinations.

Test signals: memory allocator tests validate factory creation, option parsing, invalid bounds, direct constructor helper, and allocation when supported.
