# sources/storage-engines/sqlite/src/mem5.c

## Purpose

`mem5.c` implements the optional `SQLITE_ENABLE_MEMSYS5` fixed-heap allocator. Like memsys3, it serves allocations from memory supplied by `SQLITE_CONFIG_HEAP`, but it uses a buddy-allocation algorithm: request sizes are rounded to powers of two, blocks are split from larger free blocks, and adjacent free buddies are coalesced when freed. The file cites Robson's fragmentation bound and records debug/test statistics needed to evaluate allocator behavior.

## Important APIs, Types, And Functions

The minimum allocation unit is `Mem5Link`, used as the in-pool linked-list node for free blocks. `Mem5Global mem5` stores the atom size, block count, pool pointer, mutex, debug/test allocation statistics, power-of-two freelist roots (`aiFreelist`), and one-byte-per-block control array (`aCtrl`). Control bytes store `CTRL_LOGSIZE` and `CTRL_FREE`. Helper macros and functions include `MEM5LINK`, `memsys5Unlink`, `memsys5Link`, `memsys5Enter`, `memsys5Leave`, `memsys5Size`, `memsys5MallocUnsafe`, `memsys5FreeUnsafe`, `memsys5Malloc`, `memsys5Free`, `memsys5Realloc`, `memsys5Roundup`, `memsys5Log`, `memsys5Init`, and `memsys5Shutdown`. External entry points are `sqlite3Memsys5Dump()` under `SQLITE_TEST` and `sqlite3MemGetMemsys5()`.

## Control Flow

Initialization disables the mutex temporarily, reads `sqlite3GlobalConfig.pHeap`, `nHeap`, and `mnReq`, computes `szAtom` as a power of two large enough for both the configured minimum request and `Mem5Link`, divides the heap between payload atoms and the control array, clears freelists, then decomposes the available block count into free power-of-two chunks from largest to smallest. If memstatus is disabled, it allocates its own static memory mutex.

Allocation rejects requests above 1 GiB, records max request in debug/test builds, rounds up from `szAtom` to the next power-of-two full size, finds the first freelist at that size or larger, unlinks one larger block, repeatedly splits it while linking the right-hand buddies onto smaller freelists, marks the selected block checked out, updates allocation statistics, optionally fills memory with `0xAA`, and returns the pool pointer. Freeing marks the block free, updates current stats, finds the buddy based on block index and log size, coalesces while the buddy is free and the same size, fills freed memory with `0x55` in debug builds, and links the final coalesced block. Realloc keeps the same pointer when the new rounded size fits in the existing block; otherwise it allocates, copies, and frees.

## State And Persistence Behavior

There is no on-disk persistence. The allocator state persists in the supplied heap and in `mem5`: freelist roots, block control bytes, current and highwater stats, and maximum request. The fixed heap cannot be resized after initialization. The control array is stored at the end of the same supplied memory region after the atom pool, so heap sizing directly controls both usable memory and metadata capacity.

## Dependencies And Integration Points

`mem5.c` depends on `sqliteInt.h`, SQLite global heap configuration, mutexes, `sqlite3_log()` for allocation failure logging, and the `sqlite3_mem_methods` interface. It is selected by `sqlite3_config(SQLITE_CONFIG_HEAP, ...)` in `main.c` when `SQLITE_ENABLE_MEMSYS5` is compiled. The higher `malloc.c` layer performs public API normalization, accounting, soft/hard heap limit behavior, and OOM propagation around these low-level methods.

## Risks And Edge Cases

Internal fragmentation is expected because every request rounds to a power of two. The configured minimum request (`mnReq`) and `sizeof(Mem5Link)` determine `szAtom`; too large a minimum wastes memory, while too small is rounded up. The 1 GiB allocation ceiling returns zero from `memsys5Roundup()` or `memsys5MallocUnsafe()`. Control-byte corruption can make free coalescing unsafe. Buddy coalescing depends on correct block alignment and log-size metadata. Debug/test statistics are compile-conditional, so production code cannot rely on dump counters. As with memsys3, compiling the allocator does not activate it unless heap configuration selects it.

## Test Signals

Tests should cover fixed-heap initialization with different `mnReq` values, power-of-two rounding, split allocation from larger blocks, exact freelist reuse, buddy coalescing across free order permutations, oversize allocation rejection, realloc no-move and growth-copy paths, debug memory fill patterns, `sqlite3Memsys5Dump()` freelist/stat output in test builds, and end-to-end memory status through `malloc.c`.
