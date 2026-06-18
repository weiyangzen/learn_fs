# sources/sync-backup/casync/src/mempool.h

Purpose: declares the shared pool state and the macro that generates type-specific allocation functions.

Important APIs/types/functions: `struct mempool` contains backing pools, freelist, tile size, and batch size. `DEFINE_MEMPOOL(pool_name, tile_type, alloc_at_least)` creates a static allocator that initializes size metadata and calls `mempool_alloc_tile`. `mempool_free_tile` and `mempool_drop` handle return and teardown.

Control flow/state: pool state is caller-owned and persists until `mempool_drop`; individual generated allocators lazily initialize `tile_size`/`at_least` on each call so zero-initialized structs are valid.

Dependencies/integration: intended for source-local object caches where callers can store `struct mempool` in a larger context.

Risks/test signals: the macro hides allocation failure paths and assumes the requested type is stable for the lifetime of the pool. There is no direct test in this subset; confidence comes from consumers that allocate parser/matcher nodes.

Source research group: `subset-b-009122`.
