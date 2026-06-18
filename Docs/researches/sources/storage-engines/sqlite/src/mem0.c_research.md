# sources/storage-engines/sqlite/src/mem0.c

## Purpose

`mem0.c` provides a no-op low-level allocator for builds compiled with `SQLITE_ZERO_MALLOC`. It is intentionally nonfunctional: every allocation and reallocation fails, size queries return zero, and free/shutdown calls do nothing. Its role is to provide placeholder `sqlite3_mem_methods` so an application can install a real allocator through `sqlite3_config(SQLITE_CONFIG_MALLOC, ...)` before `sqlite3_initialize()`.

## Important APIs, Types, And Functions

All allocator methods are static except `sqlite3MemSetDefault()`. The method table contains `sqlite3MemMalloc`, `sqlite3MemFree`, `sqlite3MemRealloc`, `sqlite3MemSize`, `sqlite3MemRoundup`, `sqlite3MemInit`, and `sqlite3MemShutdown`. `sqlite3MemSetDefault()` builds a static `sqlite3_mem_methods` object and passes it to `sqlite3_config(SQLITE_CONFIG_MALLOC, &defaultMethods)`.

## Control Flow

The file is compiled only under `SQLITE_ZERO_MALLOC`. If selected as the default allocator, `sqlite3MallocInit()` in `malloc.c` eventually calls `sqlite3MemSetDefault()`, causing the global allocator table to point at these stubs. Initialization returns `SQLITE_OK`, so the library can initialize structurally, but any actual heap request through `sqlite3Malloc()` or public `sqlite3_malloc()` receives NULL. Because allocation failure is immediate and universal, ordinary SQLite operation cannot proceed unless the host application replaces the allocator first.

## State And Persistence Behavior

There is no allocator-local state and no persistent data. `xRoundup` returns the requested size unchanged, but `xMalloc` and `xRealloc` never reserve memory. Since no allocation succeeds, there is no ownership to track and `xFree` is a no-op. SQLite global state may still record the method table, but no memory pool, freelist, or size metadata exists in this module.

## Dependencies And Integration Points

The only dependency is `sqliteInt.h` for SQLite types, `sqlite3_mem_methods`, constants, and `sqlite3_config()`. The integration point is the same low-level allocator contract used by all allocator backends. This file relies on the higher-level allocator wrapper in `malloc.c` to handle public API semantics, status counters, and OOM propagation.

## Risks And Edge Cases

The intended risk is explicit: if an application builds with `SQLITE_ZERO_MALLOC` and forgets to configure a usable allocator before initialization, nearly all SQLite operations fail with OOM symptoms. Because `xInit` returns success, failure is deferred until the first allocation. `xSize` returning zero is only safe because no valid allocation can originate from this allocator. This backend is unsuitable for production by itself.

## Test Signals

Tests should verify that a `SQLITE_ZERO_MALLOC` build can accept a replacement allocator via `sqlite3_config(SQLITE_CONFIG_MALLOC, ...)` before initialization and that leaving the placeholder installed causes allocation APIs to return NULL without crashing. It is also useful to assert that `sqlite3MemSetDefault()` registers exactly these stubs and that repeated free/shutdown calls are harmless.
