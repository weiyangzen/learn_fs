# sources/storage-engines/sqlite/src/mem3.c

## Purpose

`mem3.c` implements the optional `SQLITE_ENABLE_MEMSYS3` fixed-heap allocator. It avoids system `malloc()` after initialization by allocating from a caller-supplied heap configured with `SQLITE_CONFIG_HEAP`. The allocator uses 8-byte `Mem3Block` units, boundary-tag chunk headers, exact small freelists, hashed larger freelists, and a special "key chunk" that tracks the largest free region for efficient tail carving.

## Important APIs, Types, And Functions

The core type is `Mem3Block`, whose first block in a chunk stores `prevSize` and `size4x` flags and whose second block stores freelist links when the chunk is free. `Mem3Global mem3` stores the pool pointer and size, alarm reentry guard, mutex, key-chunk index and size, minimum observed key size, small freelist roots (`aiSmall`) and hash freelist roots (`aiHash`). Static helpers include `memsys3UnlinkFromList`, `memsys3Unlink`, `memsys3LinkIntoList`, `memsys3Link`, `memsys3Enter`, `memsys3Leave`, `memsys3OutOfMemory`, `memsys3Checkout`, `memsys3FromKeyBlk`, `memsys3Merge`, `memsys3MallocUnsafe`, `memsys3FreeUnsafe`, `memsys3Size`, `memsys3Roundup`, `memsys3Malloc`, `memsys3Free`, `memsys3Realloc`, `memsys3Init`, and `memsys3Shutdown`. External entry points are `sqlite3Memsys3Dump()` in debug builds and `sqlite3MemGetMemsys3()`, which returns the method table.

## Control Flow

Initialization requires `sqlite3GlobalConfig.pHeap`; otherwise `memsys3Init()` returns `SQLITE_ERROR`. It maps the supplied heap to `mem3.aPool`, computes `nPool`, and initializes one large key chunk covering the pool with sentinel metadata at the end. Allocation converts bytes to a block count, with a minimum two-block chunk. `memsys3MallocUnsafe()` first looks for an exact-size chunk in the small freelist or hashed freelist. If not found, it carves the tail from the key chunk if large enough. If the key chunk is too small, it repeatedly triggers `sqlite3_release_memory()`, temporarily links the key chunk, scans all freelists to coalesce adjacent free chunks via `memsys3Merge()`, selects the largest free chunk as the new key chunk, unlinks it, and tries tail carving again. Failure returns NULL.

Freeing marks the checked-out chunk free, updates boundary tags, links it into the appropriate freelist, and then attempts to expand the key chunk by coalescing adjacent free chunks around the existing key chunk. Reallocation keeps the old pointer when the new size is no larger than the old size and within 128 bytes of it; otherwise it allocates a new chunk, copies the overlap, and frees the old chunk. Size and roundup functions translate between user bytes and internal chunk sizes while omitting the header block overhead.

## State And Persistence Behavior

All allocator state lives inside `mem3` and the caller-provided heap. The heap is fixed after `sqlite3_initialize()`; `sqlite3_config(SQLITE_CONFIG_HEAP, ...)` changes only before initialization. No disk persistence exists. Fragmentation state persists as freelist membership, boundary tags, and key-chunk metadata. Debug dumps can inspect chunk layout, free lists, key chunk, current estimated use, and max use inferred from the minimum key block.

## Dependencies And Integration Points

`mem3.c` depends on `sqliteInt.h`, SQLite mutexes, `sqlite3GlobalConfig.pHeap/nHeap`, `sqlite3_release_memory()`, and the `sqlite3_mem_methods` interface. It is selected by `sqlite3_config(SQLITE_CONFIG_HEAP, ...)` in `main.c` when `SQLITE_ENABLE_MEMSYS3` is compiled. `malloc.c` remains the higher-level wrapper responsible for public API semantics, memory status, and hard/soft limits.

## Risks And Edge Cases

This allocator is pointer-arithmetic intensive. Corrupt boundary tags, incorrect `prevSize`, or wrong checked-out/free bits can break coalescing and freelists. The key chunk is intentionally not normally on a freelist, so code that temporarily links and unlinks it must be exact. The allocation retry loop depends on `sqlite3_release_memory()` and avoids recursive alarms with `alarmBusy`. Heap size must leave at least two sentinel blocks; misconfigured or unaligned heap memory can violate assumptions. Realloc's "within 128 bytes" no-move behavior may leave internal fragmentation. The allocator is not selected merely by compiling it; it must be configured.

## Test Signals

Useful tests include configuring a fixed heap and verifying allocations proceed without system malloc, exact small-size freelist reuse, large hash-list reuse, key-chunk tail carving, coalescing after frees, allocation failure after exhausting the heap, retry after page-cache memory release, realloc no-move and move paths, debug dump consistency checks, and status accounting through the higher `malloc.c` layer.
