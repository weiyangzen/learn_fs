# sources/test-tools/fio/smalloc.h

## Purpose
`smalloc.h` declares fio's shared-memory allocation API.

## Important APIs, Types, And Functions
It exports `smalloc(size_t)`, `scalloc(size_t, size_t)`, `sfree(void *)`, `smalloc_strdup(const char *)`, `sinit()`, `scleanup()`, `smalloc_debug(size_t)`, and the configurable `smalloc_pool_size`.

## Control Flow
Users initialize the allocator with `sinit()` before shared allocations, allocate zeroed memory with `smalloc()` or `scalloc()`, release with `sfree()`, and call `scleanup()` during shutdown.

## State And Persistence Behavior
The header exposes only the pool-size knob. The implementation owns all pool state and uses mmap-backed memory rather than durable storage.

## Dependencies And Integration Points
Consumers include server transport objects, stats aggregation arrays, and any fio code needing allocations visible across process boundaries.

## Risks And Edge Cases
The API resembles libc but ownership is distinct: `sfree()` must be used for `smalloc` memory. `scalloc()` has libc-like parameters but the implementation does not guarantee overflow checking. Callers must handle NULL returns.

## Test Signals
Compile coverage should verify all users include this header rather than redeclaring allocator APIs. Runtime tests should verify initialization ordering and correct free-family use.
