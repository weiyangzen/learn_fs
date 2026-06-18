# sources/storage-engines/pebble/internal/cache/block_map.go

Purpose: Wraps a Swiss hash map specialized for block-cache key to entry mappings with manual allocation and leak checking.

APIs and types: `blockMap`, `newBlockMap`, `Init`, `Close`, `findByValue`, `blockMapAllocator`, `fibonacciHash`, and `blockMapOptions`.

Control flow and state: The allocator obtains and frees map group storage through Pebble manual memory. The map uses a custom Fibonacci-style hash over handle ID, file number, and offset, a max bucket capacity, and the allocator. `Close` releases Swiss map memory and marks the map closed; invariant finalizer exits if a map is leaked.

Persistence and dependencies: Runtime cache index only; no persistence. Depends on `swiss`, `manual`, unsafe, and invariants.

Integration points: Used by cache shards to map block keys to cache entries while avoiding Go heap overhead.

Risks: Manual allocation requires `Close` exactly once. Unsafe conversions must match Swiss group layout. `findByValue` scans the map and is for diagnostics/invariant checks, not hot path.

Test signals: `block_map_test.go` benchmarks Swiss map behavior against Go maps; functional coverage is primarily through cache tests outside this subset.
